"""
Pytest configuration and shared fixtures for Blog service tests.
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
    if not os.getenv("DB_URL") or not os.getenv("SERVICE_ROLE_KEY"):
        pytest.skip("Supabase credentials not set - skipping tests requiring database")
    
    yield
    
    # Cleanup after tests
    pass


@pytest.fixture
def sample_post():
    """Sample blog post for testing."""
    return {
        "title": "Understanding Drug Interactions",
        "content": "This is a test blog post about drug interactions...",
        "author": "Dr. Test",
        "category": "Education",
        "tags": ["drugs", "safety", "interactions"]
    }


@pytest.fixture
def sample_posts_list():
    """Sample list of blog posts."""
    return [
        {
            "id": "1",
            "title": "Drug Safety 101",
            "content": "Introduction to drug safety...",
            "author": "Dr. Smith",
            "category": "Education",
            "created_at": "2026-01-01T00:00:00Z"
        },
        {
            "id": "2",
            "title": "Managing Side Effects",
            "content": "How to manage medication side effects...",
            "author": "Dr. Jones",
            "category": "Tips",
            "created_at": "2026-01-02T00:00:00Z"
        }
    ]
