"""
Run script for Chat service.
"""
import sys
import os

# Add parent directory to path to find Chat module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Chat.app import create_app
from Chat import config

if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=config.SERVICE_PORT,
        debug=config.DEBUG,
        threaded=True
    )
