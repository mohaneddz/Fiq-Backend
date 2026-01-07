"""
Run script for Blog service.
"""
import sys
import os

# Add parent directory to path to find Chat module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Blog.app import create_app
from Blog.config import SERVICE_PORT, DEBUG

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=DEBUG)
