"""
HTTP client for Chat service integration.
Handles communication with the Chat service REST API.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import requests
from typing import Optional, Dict, Any
from Voice import config


class ChatClient:
    """Client for interacting with the Chat service."""
    
    def __init__(self, base_url: str = None):
        """
        Initialize Chat service client.
        
        Args:
            base_url: Base URL for Chat service (defaults to config)
        """
        self.base_url = base_url or config.CHAT_SERVICE_URL
        self.timeout = 60  # 60 second timeout for LLM responses
    
    def send_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the Chat service.
        
        Args:
            message: User message text
            user_id: Optional user identifier for history tracking
            trace_id: Optional trace ID for distributed tracing
            
        Returns:
            Response dictionary from Chat service
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}/chat"
        
        payload = {"message": message}
        if user_id:
            payload["user_id"] = user_id
        
        headers = {"Content-Type": "application/json"}
        if trace_id:
            headers["X-Trace-ID"] = trace_id
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        return response.json()
    
    def extract_response_text(self, chat_response: Dict[str, Any]) -> str:
        """
        Extract the main response text from Chat service response.
        
        Args:
            chat_response: Response dict from send_message()
            
        Returns:
            Text summary from the response
        """
        try:
            if chat_response.get("status") == "success":
                data = chat_response.get("data", {})
                response = data.get("response", {})
                
                # Extract summary as primary text
                summary = response.get("summary", "")
                return summary
            else:
                # Error response
                error = chat_response.get("error", "Unknown error")
                return f"I encountered an error: {error}"
        except Exception as e:
            return f"Failed to process response: {str(e)}"
    
    def health_check(self) -> bool:
        """
        Check if Chat service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/chat/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


# Global client instance
_chat_client = None


def get_chat_client() -> ChatClient:
    """Get or create the global Chat client instance."""
    global _chat_client
    if _chat_client is None:
        _chat_client = ChatClient()
    return _chat_client
