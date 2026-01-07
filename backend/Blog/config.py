"""
Configuration for Blog service.
Contains only constants - no secrets.
"""
import os

# Service configuration
SERVICE_NAME = "blog"
SERVICE_PORT = 5003
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Database configuration (Supabase)
# Database now uses Supabase - see shared/supabase_db.py
# Requires environment variables: DB_URL, SERVICE_ROLE_KEY

# Logging
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "shared", "logs", "blog.log")

# Blog configuration
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50
