"""
Pytest configuration and shared fixtures for Chat service tests.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests."""
    # Ensure test environment variables are set
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set - skipping tests requiring API")
    
    if not os.getenv("DB_URL") or not os.getenv("SERVICE_ROLE_KEY"):
        pytest.skip("Supabase credentials not set - skipping tests requiring database")
    
    yield
    
    # Cleanup after tests
    pass


@pytest.fixture
def mock_groq_response():
    """Mock Groq API response for testing."""
    return {
        "choices": [{
            "message": {
                "content": '{"summary": "Test summary", "risks": ["Test risk"], "what_to_do": ["Test action"], "safety": {"urgent_signs": ["Test sign"], "hotlines": ["988"]}}',
                "tool_calls": None
            }
        }]
    }
