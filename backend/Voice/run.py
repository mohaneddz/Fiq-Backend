"""
Voice service entry point.
Run this file to start the Voice service.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if __name__ == "__main__":
    try:
        from Voice.app import create_app
        from Voice import config
        
        app = create_app()
        print(f"Starting Voice service on port {config.SERVICE_PORT}")
        print(f"Chat service URL: {config.CHAT_SERVICE_URL}")
        app.run(
            host="0.0.0.0",
            port=config.SERVICE_PORT,
            debug=config.DEBUG,
            threaded=True
        )
    except ModuleNotFoundError as e:
        print(f"ERROR: Missing dependency - {e}")
        print("\nPlease install required packages:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to start Voice service - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
