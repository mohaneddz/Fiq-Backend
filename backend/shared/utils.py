"""
Shared utility functions.
"""
import os
from functools import wraps
from time import time
from typing import Callable
from dotenv import load_dotenv


def load_env():
    """Load environment variables from .env file."""
    load_dotenv()


def get_env(key: str, default: str = None) -> str:
    """Get environment variable with optional default."""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} is required but not set")
    return value


def timed(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        latency_ms = (time() - start) * 1000
        return result, latency_ms
    return wrapper


def safe_int(value: any, default: int = 0) -> int:
    """Safely convert value to int with fallback."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: any, default: float = 0.0) -> float:
    """Safely convert value to float with fallback."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
