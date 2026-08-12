"""
Configuration for Voice service.
Contains only constants - no secrets.
"""
import os

# Service configuration
SERVICE_NAME = "voice"
SERVICE_PORT = 5004
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Logging
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "shared", "logs", "voice.log")

# Chat service integration
CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://localhost:5001")

# TTS Configuration
TTS_REPO_ID = "hexgrad/Kokoro-82M"
TTS_LANG_CODE = "a"
TTS_VOICE_PATH = os.path.join(os.path.dirname(__file__), "voice", "af_nicole.pt")
TTS_SAMPLE_RATE = 24000
TTS_SPEED = 1.0

# STT Configuration
STT_MODEL = "turbo"  # Whisper v3 turbo
STT_SAMPLE_RATE = 16000  # Whisper expects 16kHz

# Audio Recording Configuration
VOICE_ACTIVATION_THRESHOLD = 0.015  # Amplitude threshold for voice activation
SILENCE_THRESHOLD = 0.01  # Amplitude threshold for silence detection
SILENCE_DURATION = 1.5  # Seconds of silence to end recording
INTERRUPTION_THRESHOLD = 0.025  # Threshold to detect user interruption during TTS

# Conversation Configuration
CHAT_HISTORY_FIRST_N = 5  # Keep first N messages in context
CHAT_HISTORY_LAST_N = 10  # Keep last N messages in context
