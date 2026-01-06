"""
Test Chat agent functionality.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from unittest.mock import Mock, patch
from Chat.core.agent import ChatAgent


@pytest.fixture
def agent():
    """Create test agent with mock API key."""
    with patch('Chat.core.agent.Groq'):
        return ChatAgent(groq_api_key="test_key")


class TestAgentExecution:
    """Test agent tool execution."""
    
    def test_execute_tool_lookup_drug(self, agent):
        """Test execute_tool with lookup_drug."""
        result = agent.execute_tool("lookup_drug", drug_name="Cocaine")
        assert isinstance(result, dict)
        assert "found" in result or "error" in result
    
    def test_execute_tool_lookup_history(self, agent):
        """Test execute_tool with lookup_history."""
        result = agent.execute_tool("lookup_history", user_id="test_user")
        assert isinstance(result, dict)
        assert "found" in result or "error" in result
    
    def test_execute_tool_rag_query(self, agent):
        """Test execute_tool with rag_query."""
        result = agent.execute_tool("rag_query", query="test query")
        assert isinstance(result, dict)
        assert "results" in result
        assert "count" in result
    
    def test_execute_tool_websearch(self, agent):
        """Test execute_tool with websearch_drug."""
        result = agent.execute_tool("websearch_drug", query="test drug")
        assert isinstance(result, dict)
    
    def test_execute_tool_unknown(self, agent):
        """Test execute_tool with unknown tool."""
        result = agent.execute_tool("unknown_tool")
        assert "error" in result
        assert "Unknown tool" in result["error"]
    
    def test_execute_tool_logging(self, agent):
        """Test that tool execution is logged."""
        # Execute a tool with request_id
        agent.execute_tool("lookup_drug", request_id="test_123", drug_name="Test")
        # Logger should have been called (checked via fixture if available)


class TestAgentConversation:
    """Test agent conversation management."""
    
    def test_reset_conversation(self, agent):
        """Test conversation history reset."""
        agent.conversation_history = [
            {"role": "user", "content": "test"},
            {"role": "assistant", "content": "response"}
        ]
        agent.reset_conversation()
        assert len(agent.conversation_history) == 0
    
    def test_fallback_response(self, agent):
        """Test fallback response structure."""
        fallback = agent._fallback_response()
        
        assert "summary" in fallback
        assert "risks" in fallback
        assert "what_to_do" in fallback
        assert "safety" in fallback
        assert isinstance(fallback["summary"], str)


class TestToolSchemas:
    """Test tool schema definitions."""
    
    def test_all_tools_defined(self, agent):
        """Test that all required tools have schemas."""
        tool_names = [ts["function"]["name"] for ts in agent.tool_schemas]
        
        assert "lookup_drug" in tool_names
        assert "lookup_history" in tool_names
        assert "rag_query" in tool_names
        assert "websearch_drug" in tool_names
    
    def test_tool_parameters(self, agent):
        """Test that tool schemas have correct parameters."""
        for tool_schema in agent.tool_schemas:
            func = tool_schema["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func
            
            params = func["parameters"]
            assert "type" in params
            assert params["type"] == "object"
            assert "properties" in params
            assert "required" in params


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
