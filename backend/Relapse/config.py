"""
Configuration for Relapse service.
Contains only constants - no secrets.
"""
import os

# Service configuration
SERVICE_NAME = "relapse"
SERVICE_PORT = 5002
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Logging
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "shared", "logs", "relapse.log")

# Model configuration
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "relapse_model.pkl")
MODEL_VERSION_FILE = os.path.join(MODEL_DIR, "version.json")

# Feature engineering parameters
CRAVING_WINDOW_DAYS = 7  # Rolling window for craving trend
SLEEP_WINDOW_DAYS = 7  # Window for sleep deviation
TRIGGER_WINDOW_DAYS = 7  # Window for trigger count

# Model parameters
RANDOM_STATE = 42
TEST_SIZE = 0.2
N_ESTIMATORS = 100
MAX_DEPTH = 5
LEARNING_RATE = 0.1
