"""
Flask application factory for Chat service.
"""
import sys
import os
from flask import Flask
from flask_cors import CORS

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.utils import load_env
from shared.logging import JSONLogger
from Chat import config


def create_app():
    """Create and configure Flask app."""
    load_env()
    
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    # Enable CORS
    CORS(app)
    
    # Initialize logger
    app.logger_instance = JSONLogger(config.LOG_FILE, config.SERVICE_NAME)
    
    # Register blueprints
    from Chat.api.routes import chat_bp
    app.register_blueprint(chat_bp)
    
    return app
