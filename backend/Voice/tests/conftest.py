"""
Pytest configuration and shared fixtures for Voice service tests.
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
    # Test environment setup (can be used for initialization)
    yield
    
    # Cleanup after tests
    pass


@pytest.fixture
def chat_service_available():
    """Check if Chat service is available."""
    if not os.getenv("CHAT_SERVICE_URL"):
        pytest.skip("CHAT_SERVICE_URL not set - skipping test requiring Chat service")
    return True


@pytest.fixture
def sample_audio_data():
    """Sample audio data for testing."""
    import numpy as np
    # Generate 1 second of silence at 16kHz
    duration = 1.0
    sample_rate = 16000
    audio = np.zeros(int(duration * sample_rate), dtype=np.float32)
    return audio, sample_rate


@pytest.fixture
def sample_text():
    """Sample text for testing TTS."""
    return "Hello, this is a test message for the voice service."
