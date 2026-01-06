"""
Configuration for Chat service.
Contains only constants - no secrets.
"""
import os

# Service configuration
SERVICE_NAME = "chat"
SERVICE_PORT = 5001
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Database paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DRUGS_DB_PATH = os.path.join(DATA_DIR, "drugs.db")
HISTORY_DB_PATH = os.path.join(DATA_DIR, "history.db")

# Logging
LOG_FILE = os.path.join(os.path.dirname(__file__), "history.log")

# LLM configuration
LLM_MODEL = "llama-3.3-70b-versatile"  # Groq model
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2048

# RAG configuration
VECTOR_STORE_PATH = os.path.join(DATA_DIR, "vector_store")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RAG_TOP_K = 3

# WebSearch configuration
WEBSEARCH_MAX_RESULTS = 5
WEBSEARCH_TIMEOUT = 10
