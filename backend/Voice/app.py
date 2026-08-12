"""
Flask application factory for Voice service.
"""
import sys
import os
from flask import Flask
from flask_cors import CORS

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.utils import load_env
from shared.logging import JSONLogger
from Voice import config


def create_app():
    """Create and configure Flask app."""
    load_env()
    
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file upload
    
    # Enable CORS
    CORS(app)
    
    # Initialize logger
    app.logger_instance = JSONLogger(config.LOG_FILE, config.SERVICE_NAME)
    
    # Register blueprints
    from Voice.api.routes import voice_bp
    app.register_blueprint(voice_bp, url_prefix='/voice')
    
    return app
