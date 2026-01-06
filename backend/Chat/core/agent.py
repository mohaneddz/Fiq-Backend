"""
LLM Agent orchestration using Groq tool calling (no fake tool JSON).
"""
import os
import sys
import json
from time import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from typing import Dict, Any, List, Optional

from Chat import config, prompts
from Chat.core.tools import get_tools
from Chat.core.rag import RAGEngine
from Chat.core.websearch import WebSearchTool
from shared.logging import JSONLogger


class ChatAgent:
    """Main agent orchestrator for chat service (tool-calling)."""

    def __init__(self, groq_api_key: str):
        # Clear proxy env vars that may interfere with Groq
        proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]
        saved_proxies = {}
        for var in proxy_vars:
            if var in os.environ:
                saved_proxies[var] = os.environ.pop(var)

        try:
            from groq import Groq
            self.client = Groq(api_key=groq_api_key)
        finally:
            os.environ.update(saved_proxies)

        self.tools = get_tools()
        self.rag = RAGEngine()
        self.websearch = WebSearchTool()
        self.conversation_history: List[Dict[str, str]] = []
        
        # Initialize logger with correct parameters
        log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        log_file = os.path.join(log_dir, "chat.log")
        self.logger = JSONLogger(log_file=log_file, service_name="chat")

        # Groq tool schemas (OpenAI-style)
        self.tool_schemas = [
            {
                "type": "function",
                "function": {
                    "name": "lookup_drug",
                    "description": "Query drugs database for a specific substance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "drug_name": {"type": "string", "description": "Drug name to look up"}
                        },
                        "required": ["drug_name"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "lookup_history",
                    "description": "Retrieve medical/recovery encounter history for a user.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User identifier"}
                        },
                        "required": ["user_id"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "rag_query",
                    "description": "Semantic search over internal drug knowledge base.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "websearch_drug",
                    "description": "Web search fallback for current drug information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query / drug name"}
                        },
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                },
            },
        ]

    def chat(self, user_message: str, user_id: Optional[str] = None, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Full agent execution:
        - LLM decides tools
        - tools executed internally
        - returns final JSON object ONLY (no tool traces)
        """
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": user_message})

            # Build messages
            messages: List[Dict[str, Any]] = [
                {"role": "system", "content": prompts.SYSTEM_PROMPT},
                *self.conversation_history,
            ]

            # If user_id exists, expose it as context (no tool call yet)
            if user_id:
                messages.append(
                    {"role": "system", "content": f"Context: user_id={user_id}"}
                )

            # Tool-calling loop
            max_rounds = 3
            last_assistant_content = None

            for _ in range(max_rounds):
                resp = self.client.chat.completions.create(
                    model=config.LLM_MODEL,
                    messages=messages,
                    temperature=config.LLM_TEMPERATURE,
                    max_tokens=config.LLM_MAX_TOKENS,
                    tools=self.tool_schemas,
                    tool_choice="auto",
                )

                msg = resp.choices[0].message
                last_assistant_content = getattr(msg, "content", None)

                tool_calls = getattr(msg, "tool_calls", None)
                if not tool_calls:
                    # No more tool calls; assistant should output final JSON now
                    break

                # Append assistant message (with tool calls) to internal message list
                messages.append(
                    {
                        "role": "assistant",
                        "content": msg.content or "",
                        "tool_calls": tool_calls,
                    }
                )

                # Execute each tool call and append tool results
                for tc in tool_calls:
                    fn = tc.function.name
                    args = json.loads(tc.function.arguments or "{}")

                    # Auto-inject user_id if tool asks history but args missing
                    if fn == "lookup_history" and (not args.get("user_id")) and user_id:
                        args["user_id"] = user_id

                    result = self.execute_tool(fn, request_id=request_id, **args)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(result, ensure_ascii=False),
                        }
                    )

            # Now parse final JSON response
            final_obj = self._safe_parse_final_json(last_assistant_content, messages)

            # Store assistant content in conversation history (optional)
            self.conversation_history.append(
                {"role": "assistant", "content": json.dumps(final_obj, ensure_ascii=False)}
            )

            return {
                "response": final_obj,
                "conversation_history": self.conversation_history,
            }

        except Exception as e:
            return {
                "error": str(e),
                "response": {
                    "summary": "Request failed due to an internal error.",
                    "risks": [],
                    "what_to_do": ["Try again later."],
                    "safety": {
                        "urgent_signs": ["Trouble breathing", "Unresponsiveness"],
                        "hotlines": ["988", "1-800-662-4357"],
                    },
                },
            }

    def execute_tool(self, tool_name: str, request_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute a specific tool by name with logging."""
        start_time = time()
        status = "success"
        result = None
        
        # Sanitize args for logging (remove sensitive data if needed)
        log_args = {
            k: v if k not in ["user_id"] else "***" for k, v in kwargs.items() if k != "request_id"
        }
        
        try:
            if tool_name == "lookup_drug":
                result = self.tools["lookup_drug"].run(kwargs.get("drug_name", ""))

            elif tool_name == "lookup_history":
                result = self.tools["lookup_history"].run(kwargs.get("user_id", ""))

            elif tool_name == "rag_query":
                results = self.rag.query(kwargs.get("query", ""))
                result = {"results": results, "count": len(results)}

            elif tool_name == "websearch_drug":
                q = kwargs.get("query", "")
                result = self.websearch.run(q)
            
            else:
                status = "error"
                result = {"error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            status = "error"
            result = {"error": str(e)}
        
        finally:
            # Log tool execution
            latency_ms = (time() - start_time) * 1000
            self.logger.log_request(
                request_id=request_id or "unknown",
                endpoint="execute_tool",
                tool=tool_name,
                status=status,
                latency_ms=round(latency_ms, 2),
                metadata={
                    "args": log_args
                }
            )
        
        return result

    def _safe_parse_final_json(self, content: Optional[str], messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse assistant final JSON; repair once if invalid."""
        if not content:
            return self._fallback_response()

        try:
            obj = json.loads(content)
            # Support either { "response": {...} } or direct {...}
            if "response" in obj and isinstance(obj["response"], dict):
                return obj["response"]
            if "summary" in obj:
                return obj
        except Exception:
            pass

        # One repair attempt
        repair_messages = messages + [
            {
                "role": "system",
                "content": "Return ONLY valid JSON matching the required schema. No markdown.",
            }
        ]
        resp2 = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=repair_messages,
            temperature=0,
            max_tokens=config.LLM_MAX_TOKENS,
        )
        repaired = resp2.choices[0].message.content or ""
        try:
            obj = json.loads(repaired)
            if "response" in obj and isinstance(obj["response"], dict):
                return obj["response"]
            if "summary" in obj:
                return obj
        except Exception:
            return self._fallback_response()

        return self._fallback_response()

    def _fallback_response(self) -> Dict[str, Any]:
        return {
            "summary": "Unable to format response safely.",
            "risks": [],
            "what_to_do": ["Consult a healthcare professional."],
            "safety": {
                "urgent_signs": ["Trouble breathing", "Unresponsiveness"],
                "hotlines": ["988", "1-800-662-4357"],
            },
        }

    def reset_conversation(self):
        self.conversation_history = []
