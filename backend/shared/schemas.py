"""
Common response schemas for cross-service contract.
"""
from typing import Any, Optional
from dataclasses import dataclass, asdict
import uuid


@dataclass
class APIResponse:
    """Standard API response format."""
    request_id: str
    status: str  # "success" or "error"
    data: Optional[Any] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def success(cls, data: Any, request_id: Optional[str] = None):
        """Create a success response."""
        return cls(
            request_id=request_id or str(uuid.uuid4()),
            status="success",
            data=data,
            error=None
        )
    
    @classmethod
    def error(cls, error_message: str, request_id: Optional[str] = None):
        """Create an error response."""
        return cls(
            request_id=request_id or str(uuid.uuid4()),
            status="error",
            data=None,
            error=error_message
        )


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())
