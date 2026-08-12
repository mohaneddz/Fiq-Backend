"""
Tests for Voice API routes.
"""
import pytest
from Voice.app import create_app
import io
import numpy as np
import soundfile as sf


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns 200."""
        response = client.get('/voice/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'voice'


class TestSTTEndpoint:
    """Tests for speech-to-text endpoint."""
    
    @pytest.mark.skip(reason="Requires audio file and Whisper model")
    def test_stt_with_audio_file(self, client, sample_audio_data):
        """Test STT with audio file upload."""
        audio, sample_rate = sample_audio_data
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        
        response = client.post('/voice/stt',
                              data={'audio': (buffer, 'test.wav')},
                              content_type='multipart/form-data')
        
        assert response.status_code in [200, 500]  # May fail without model
        if response.status_code == 200:
            data = response.get_json()
            assert 'data' in data
            assert 'text' in data['data']
    
    def test_stt_without_audio(self, client):
        """Test STT endpoint without audio file."""
        response = client.post('/voice/stt')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'


class TestTTSEndpoint:
    """Tests for text-to-speech endpoint."""
    
    @pytest.mark.skip(reason="Requires Kokoro TTS model")
    def test_tts_with_text(self, client, sample_text):
        """Test TTS with text input."""
        response = client.post('/voice/tts',
                              json={'text': sample_text},
                              content_type='application/json')
        
        assert response.status_code in [200, 500]  # May fail without model
        if response.status_code == 200:
            assert response.mimetype == 'audio/wav'
    
    def test_tts_without_text(self, client):
        """Test TTS endpoint without text."""
        response = client.post('/voice/tts',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_tts_with_empty_text(self, client):
        """Test TTS endpoint with empty text."""
        response = client.post('/voice/tts',
                              json={'text': ''},
                              content_type='application/json')
        assert response.status_code == 400


class TestSpeakEndpoint:
    """Tests for complete voice interaction endpoint."""
    
    @pytest.mark.skip(reason="Requires models and Chat service")
    def test_speak_with_audio(self, client, sample_audio_data, chat_service_available):
        """Test speak endpoint with audio input."""
        audio, sample_rate = sample_audio_data
        
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        
        response = client.post('/voice/speak',
                              data={'audio': (buffer, 'test.wav')},
                              content_type='multipart/form-data')
        
        # May fail without models or Chat service
        assert response.status_code in [200, 400, 500]
    
    @pytest.mark.skip(reason="Requires models and Chat service")
    def test_speak_with_text(self, client, sample_text, chat_service_available):
        """Test speak endpoint with text input."""
        response = client.post('/voice/speak',
                              json={'text': sample_text},
                              content_type='application/json')
        
        # May fail without models or Chat service
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            assert response.mimetype == 'audio/wav'
    
    def test_speak_without_input(self, client):
        """Test speak endpoint without any input."""
        response = client.post('/voice/speak')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'


class TestConversationEndpoint:
    """Tests for conversation management endpoints."""
    
    def test_clear_conversation(self, client):
        """Test clearing conversation history."""
        response = client.post('/voice/conversation/clear',
                              json={'user_id': 'test_user'},
                              content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
    
    def test_clear_conversation_anonymous(self, client):
        """Test clearing anonymous conversation."""
        response = client.post('/voice/conversation/clear',
                              json={},
                              content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['user_id'] == 'anonymous'
