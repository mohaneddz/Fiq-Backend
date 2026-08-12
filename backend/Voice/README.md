# Voice API Guide

The Voice service provides speech-to-text (STT), text-to-speech (TTS), and full voice conversation capabilities. It integrates with the Chat service for conversational AI.

## Getting Started

### Prerequisites
- Python 3.8+
- Required packages: `pip install -r requirements.txt`

### Running the Service
```bash
python run.py
```
The service runs on `http://localhost:5004` by default.

## API Endpoints

All endpoints are prefixed with `/voice`.

### Health Check
- **GET** `/voice/health`
- **Description**: Check if the service is running
- **Response**: JSON with service status

```json
{
  "status": "healthy",
  "service": "voice",
  "timestamp": 1704652800,
  "chat_service": "http://localhost:5001"
}
```

### Speech to Text (STT)
- **POST** `/voice/stt`
- **Description**: Convert audio file to text
- **Request**: Multipart form with `audio` file (WAV, MP3, etc.)
- **Response**: JSON with transcribed text

**Example Request:**
```bash
curl -X POST -F "audio=@audio.wav" http://localhost:5004/voice/stt
```

**Response:**
```json
{
  "success": true,
  "data": {
    "text": "Hello, how are you?",
    "audio_duration": 2.5
  },
  "request_id": "req_123456"
}
```

### Text to Speech (TTS)
- **POST** `/voice/tts`
- **Description**: Convert text to audio
- **Request**: JSON with `text` field
- **Response**: WAV audio file

**Example Request:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!"}' \
  http://localhost:5004/voice/tts \
  -o response.wav
```

### Full Voice Conversation
- **POST** `/voice/speak`
- **Description**: Complete voice interaction - transcribes input, sends to Chat service, returns TTS audio
- **Request**: Either audio file upload or JSON with `text` field. Optional `user_id` for conversation context
- **Response**: WAV audio file with spoken response

**Example with audio:**
```bash
curl -X POST -F "audio=@input.wav" -F "user_id=user123" \
  http://localhost:5004/voice/speak \
  -o response.wav
```

**Example with text:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"text": "Hello", "user_id": "user123"}' \
  http://localhost:5004/voice/speak \
  -o response.wav
```

### Clear Conversation
- **POST** `/voice/conversation/clear`
- **Description**: Clear conversation history for a user
- **Request**: JSON with optional `user_id`
- **Response**: JSON confirmation

**Example Request:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}' \
  http://localhost:5004/voice/conversation/clear
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Conversation history cleared",
    "user_id": "user123"
  },
  "request_id": "req_123456"
}
```

## Error Handling

All endpoints return errors in the following format:
```json
{
  "success": false,
  "error": "Error message",
  "request_id": "req_123456"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad request (missing parameters, invalid input)
- `500`: Internal server error

## Configuration

Key settings in `config.py`:
- `SERVICE_PORT`: 5004 (default)
- `CHAT_SERVICE_URL`: URL of the Chat service
- `TTS_VOICE_PATH`: Path to TTS voice model
- `STT_MODEL`: Whisper model for STT

## Dependencies

- Flask: Web framework
- soundfile: Audio file handling
- librosa: Audio processing
- Kokoro-82M: TTS model
- Whisper: STT model
- Chat service integration</content>
<parameter name="filePath">d:\Programming\AI\Hackathons\.Competitions\Drugs\backend\Voice\README.md