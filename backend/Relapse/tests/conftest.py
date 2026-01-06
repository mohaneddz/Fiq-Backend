"""
Pytest configuration and shared fixtures for Relapse service tests.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import numpy as np


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests."""
    # Set random seed for reproducibility
    np.random.seed(42)
    
    yield
    
    # Cleanup after tests
    pass


@pytest.fixture
def sample_features():
    """Sample feature vector for testing."""
    return np.array([[
        30.0,    # days_clean
        3.5,     # craving_trend
        1.2,     # sleep_deviation
        1.0,     # trigger_count
        2.0,     # support_sessions
        90.0     # medication_adherence
    ]])


@pytest.fixture
def sample_training_data():
    """Sample training data for model testing."""
    X = np.random.rand(100, 6)
    y = np.random.randint(1, 100, 100)
    return X, y
