"""
API routes for Chat service.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from flask import Blueprint, request, jsonify, current_app
from time import time
from shared.schemas import APIResponse, generate_request_id
from shared.utils import get_env, safe_int
from Chat.core.agent import ChatAgent
from Chat.core.rag import RAGEngine
from typing import Dict, Any

chat_bp = Blueprint('chat', __name__)


def validate_response_schema(response: Dict[str, Any]) -> Dict[str, Any]:
    """Validate response has required schema, return fallback if invalid."""
    try:
        # Check top-level keys
        if not isinstance(response, dict):
            return get_fallback_response()
        
        # Validate required fields
        if "summary" not in response or not isinstance(response["summary"], str):
            return get_fallback_response()
        
        if "risks" not in response or not isinstance(response["risks"], list):
            return get_fallback_response()
        
        if "what_to_do" not in response or not isinstance(response["what_to_do"], list):
            return get_fallback_response()
        
        # Validate safety object
        if "safety" not in response or not isinstance(response["safety"], dict):
            return get_fallback_response()
        
        safety = response["safety"]
        if "urgent_signs" not in safety or not isinstance(safety["urgent_signs"], list):
            return get_fallback_response()
        
        if "hotlines" not in safety or not isinstance(safety["hotlines"], list):
            return get_fallback_response()
        
        # All validations passed
        return response
    
    except Exception:
        return get_fallback_response()


def get_fallback_response() -> Dict[str, Any]:
    """Return safe fallback response when validation fails."""
    return {
        "summary": "Unable to process request safely. Please consult a healthcare professional.",
        "risks": ["Response validation failed"],
        "what_to_do": [
            "Contact a healthcare provider for guidance",
            "Call 988 for immediate crisis support"
        ],
        "safety": {
            "urgent_signs": [
                "Trouble breathing",
                "Unresponsiveness",
                "Chest pain",
                "Severe confusion"
            ],
            "hotlines": ["988", "1-800-662-4357"]
        }
    }

# Initialize components
_agent = None
_rag = None


def get_agent():
    """Lazy initialize agent."""
    global _agent
    if _agent is None:
        groq_api_key = get_env("GROQ_API_KEY", "")
        _agent = ChatAgent(groq_api_key)
    return _agent


def get_rag():
    """Lazy initialize RAG engine."""
    global _rag
    if _rag is None:
        _rag = RAGEngine()
    return _rag


@chat_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    request_id = generate_request_id()
    return jsonify(APIResponse.success(
        data={"status": "healthy", "service": "chat"},
        request_id=request_id
    ).to_dict())


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint with full agent execution."""
    request_id = generate_request_id()
    trace_id = request_id  # Use request_id as trace_id for the session
    start_time = time()
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = data.get('user_id')
        
        if not user_message:
            return jsonify(APIResponse.error(
                "Message is required",
                request_id=request_id
            ).to_dict()), 400
        
        # Execute agent with trace_id
        agent = get_agent()
        result = agent.chat(user_message, user_id=user_id, request_id=request_id, trace_id=trace_id)
        
        # Validate response schema
        if "response" in result and isinstance(result["response"], dict):
            result["response"] = validate_response_schema(result["response"])
        else:
            # Fallback if response structure is completely wrong
            result["response"] = get_fallback_response()
        
        # Calculate result size
        import sys, json
        result_size = sys.getsizeof(json.dumps(result))
        
        # Log request (only once, not duplicate)
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            trace_id=trace_id,
            endpoint="/chat",
            status="success",
            status_code=200,
            latency_ms=latency_ms,
            result_size_bytes=result_size
        )
        
        return jsonify(APIResponse.success(
            data=result,
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            trace_id=trace_id,
            endpoint="/chat",
            status="error",
            status_code=500,
            latency_ms=latency_ms,
            error=str(e),
            error_code="CHAT_ERROR",
            error_type=type(e).__name__
        )
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500


@chat_bp.route('/chat/rag/query', methods=['POST'])
def rag_query():
    """RAG-only retrieval endpoint."""
    request_id = generate_request_id()
    start_time = time()
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 3)
        
        if not query:
            return jsonify(APIResponse.error(
                "Query is required",
                request_id=request_id
            ).to_dict()), 400
        
        # Execute RAG query
        rag = get_rag()
        results = rag.query(query, top_k=top_k)
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/chat/rag/query",
            tool="rag_query",
            status="success",
            latency_ms=latency_ms
        )
        
        return jsonify(APIResponse.success(
            data={"results": results, "count": len(results)},
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/chat/rag/query",
            tool="rag_query",
            status="error",
            latency_ms=latency_ms,
            error=str(e)
        )
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500


@chat_bp.route('/chat/tools/drug_lookup', methods=['POST'])
def drug_lookup():
    """Drug lookup tool endpoint."""
    request_id = generate_request_id()
    start_time = time()
    
    try:
        data = request.get_json()
        drug_name = data.get('drug_name', '')
        
        if not drug_name:
            return jsonify(APIResponse.error(
                "drug_name is required",
                request_id=request_id
            ).to_dict()), 400
        
        # Execute tool
        agent = get_agent()
        result = agent.execute_tool("lookup_drug", drug_name=drug_name)
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/chat/tools/drug_lookup",
            tool="lookup_drug",
            status="success",
            latency_ms=latency_ms
        )
        
        return jsonify(APIResponse.success(
            data=result,
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/chat/tools/drug_lookup",
            tool="lookup_drug",
            status="error",
            latency_ms=latency_ms,
            error=str(e)
        )
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500


@chat_bp.route('/chat/tools/history_lookup', methods=['POST'])
def history_lookup():
    """User history lookup tool endpoint."""
    request_id = generate_request_id()
    start_time = time()
    
    try:
        data = request.get_json()
        user_id = data.get('user_id', '')
        
        if not user_id:
            return jsonify(APIResponse.error(
                "user_id is required",
                request_id=request_id
            ).to_dict()), 400
        
        # Execute tool
        agent = get_agent()
        result = agent.execute_tool("lookup_history", user_id=user_id)
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/chat/tools/history_lookup",
            tool="lookup_history",
            status="success",
            latency_ms=latency_ms
        )
        
        return jsonify(APIResponse.success(
            data=result,
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/chat/tools/history_lookup",
            tool="lookup_history",
            status="error",
            latency_ms=latency_ms,
            error=str(e)
        )
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500


@chat_bp.route('/chat/websearch', methods=['POST'])
def websearch():
    """WebSearch tool endpoint."""
    request_id = generate_request_id()
    start_time = time()
    
    try:
        data = request.get_json()
        drug_name = data.get('drug_name', '')
        
        if not drug_name:
            return jsonify(APIResponse.error(
                "drug_name is required",
                request_id=request_id
            ).to_dict()), 400
        
        # Execute tool
        agent = get_agent()
        result = agent.execute_tool("websearch_drug", drug_name=drug_name)
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/chat/websearch",
            tool="websearch_drug",
            status="success",
            latency_ms=latency_ms
        )
        
        return jsonify(APIResponse.success(
            data=result,
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/chat/websearch",
            tool="websearch_drug",
            status="error",
            latency_ms=latency_ms,
            error=str(e)
        )
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500


@chat_bp.route('/chat/ingest/drugs', methods=['POST'])
def ingest_drugs():
    """Build drug vector index."""
    request_id = generate_request_id()
    start_time = time()
    
    try:
        # Execute ingestion
        rag = get_rag()
        result = rag.ingest_drugs()
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/chat/ingest/drugs",
            status="success",
            latency_ms=latency_ms
        )
        
        return jsonify(APIResponse.success(
            data=result,
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/chat/ingest/drugs",
            status="error",
            latency_ms=latency_ms,
            error=str(e)
        )
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500


@chat_bp.route('/chat/logs/tail', methods=['GET'])
def tail_logs():
    """Tail log file."""
    request_id = generate_request_id()
    
    try:
        n = safe_int(request.args.get('n', 200))
        logs = current_app.logger_instance.tail_logs(n)
        
        return jsonify(APIResponse.success(
            data={"logs": logs, "count": len(logs)},
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500
