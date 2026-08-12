"""
Conversation manager for voice interactions.
Handles message history and conversation flow.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from typing import List, Dict, Optional
from Voice import config
from Voice.core.chat_client import get_chat_client


class ConversationManager:
    """Manages conversation history and state for voice interactions."""
    
    def __init__(self, user_id: Optional[str] = None):
        """
        Initialize conversation manager.
        
        Args:
            user_id: Optional user identifier for tracking
        """
        self.user_id = user_id
        self.messages: List[Dict[str, str]] = []
        self.chat_client = get_chat_client()
    
    def add_user_message(self, message: str):
        """Add a user message to history."""
        self.messages.append({
            "role": "user",
            "content": message
        })
    
    def add_assistant_message(self, message: str):
        """Add an assistant message to history."""
        self.messages.append({
            "role": "assistant",
            "content": message
        })
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history with truncation."""
        # Keep first N and last N messages to manage context size
        if len(self.messages) <= (config.CHAT_HISTORY_FIRST_N + config.CHAT_HISTORY_LAST_N):
            return self.messages
        
        first_messages = self.messages[:config.CHAT_HISTORY_FIRST_N]
        last_messages = self.messages[-config.CHAT_HISTORY_LAST_N:]
        return first_messages + last_messages
    
    def clear_history(self):
        """Clear conversation history."""
        self.messages = []
    
    def send_message(self, message: str, trace_id: Optional[str] = None) -> Dict:
        """
        Send message to Chat service and update history.
        
        Args:
            message: User message text
            trace_id: Optional trace ID for distributed tracing
            
        Returns:
            Response dictionary from Chat service
        """
        # Add user message to history
        self.add_user_message(message)
        
        # Send to Chat service
        try:
            response = self.chat_client.send_message(
                message=message,
                user_id=self.user_id,
                trace_id=trace_id
            )
            
            # Extract and add assistant response to history
            response_text = self.chat_client.extract_response_text(response)
            self.add_assistant_message(response_text)
            
            return response
        
        except Exception as e:
            error_msg = f"Error communicating with chat service: {str(e)}"
            self.add_assistant_message(error_msg)
            raise


# Global conversation managers by user_id
_conversation_managers: Dict[str, ConversationManager] = {}


def get_conversation_manager(user_id: Optional[str] = None) -> ConversationManager:
    """
    Get or create a conversation manager for a user.
    
    Args:
        user_id: User identifier (None for anonymous)
        
    Returns:
        ConversationManager instance
    """
    key = user_id or "anonymous"
    
    if key not in _conversation_managers:
        _conversation_managers[key] = ConversationManager(user_id=user_id)
    
    return _conversation_managers[key]


def clear_conversation(user_id: Optional[str] = None):
    """Clear conversation history for a user."""
    key = user_id or "anonymous"
    if key in _conversation_managers:
        _conversation_managers[key].clear_history()
