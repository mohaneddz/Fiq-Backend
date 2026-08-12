"""
API routes for Voice service.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from flask import Blueprint, request, jsonify, current_app, send_file
from time import time
import numpy as np
import io
import soundfile as sf
from shared.schemas import APIResponse, generate_request_id
from Voice.core.stt import transcribe_audio, listen
from Voice.core.tts import generate_audio, text_to_speech, clean_text_for_tts
from Voice.core.chat_client import get_chat_client
from Voice.core.conversation import get_conversation_manager, clear_conversation
from Voice import config

voice_bp = Blueprint('voice', __name__)


@voice_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "voice",
        "timestamp": int(time()),
        "chat_service": config.CHAT_SERVICE_URL
    }), 200


@voice_bp.route('/stt', methods=['POST'])
def speech_to_text():
    """
    Convert speech to text.
    
    Request: Audio file upload (WAV, MP3, etc.)
    Response: Transcribed text
    """
    request_id = generate_request_id()
    start_time = time()
    
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            current_app.logger_instance.log_request(
                request_id=request_id,
                endpoint='/voice/stt',
                status='error',
                status_code=400,
                latency_ms=(time() - start_time) * 1000,
                error='No audio file provided'
            )
            return APIResponse.error('No audio file provided', request_id).to_dict(), 400
        
        audio_file = request.files['audio']
        
        # Read audio file
        audio_data, sample_rate = sf.read(io.BytesIO(audio_file.read()))
        
        # Convert to mono if stereo
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # Resample to 16kHz if needed (Whisper expects 16kHz)
        if sample_rate != config.STT_SAMPLE_RATE:
            import librosa
            audio_data = librosa.resample(
                audio_data,
                orig_sr=sample_rate,
                target_sr=config.STT_SAMPLE_RATE
            )
        
        # Ensure float32
        audio_data = audio_data.astype(np.float32)
        
        # Transcribe
        text = transcribe_audio(audio_data)
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/voice/stt',
            status='success',
            status_code=200,
            latency_ms=latency_ms
        )
        
        return APIResponse.success({
            'text': text,
            'audio_duration': len(audio_data) / config.STT_SAMPLE_RATE
        }, request_id).to_dict(), 200
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/voice/stt',
            status='error',
            status_code=500,
            latency_ms=latency_ms,
            error=str(e)
        )
        return APIResponse.error(str(e), request_id).to_dict(), 500


@voice_bp.route('/tts', methods=['POST'])
def text_to_speech_endpoint():
    """
    Convert text to speech.
    
    Request: JSON with 'text' field
    Response: Audio file (WAV format)
    """
    request_id = generate_request_id()
    start_time = time()
    
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            current_app.logger_instance.log_request(
                request_id=request_id,
                endpoint='/voice/tts',
                status='error',
                status_code=400,
                latency_ms=(time() - start_time) * 1000,
                error='No text provided'
            )
            return APIResponse.error('No text provided', request_id).to_dict(), 400
        
        text = data['text']
        
        # Generate audio
        audio = generate_audio(text)
        
        if len(audio) == 0:
            current_app.logger_instance.log_request(
                request_id=request_id,
                endpoint='/voice/tts',
                status='error',
                status_code=400,
                latency_ms=(time() - start_time) * 1000,
                error='Failed to generate audio'
            )
            return APIResponse.error('Failed to generate audio', request_id).to_dict(), 400
        
        # Convert to WAV file
        buffer = io.BytesIO()
        sf.write(buffer, audio, config.TTS_SAMPLE_RATE, format='WAV')
        buffer.seek(0)
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/voice/tts',
            status='success',
            status_code=200,
            latency_ms=latency_ms,
            result_size_bytes=buffer.getbuffer().nbytes
        )
        
        return send_file(
            buffer,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='response.wav'
        )
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/voice/tts',
            status='error',
            status_code=500,
            latency_ms=latency_ms,
            error=str(e)
        )
        return APIResponse.error(str(e), request_id).to_dict(), 500


@voice_bp.route('/speak', methods=['POST'])
def speak():
    """
    Complete voice interaction: audio in, audio out.
    Transcribes input, sends to Chat service, returns TTS audio.
    
    Request: Audio file upload OR JSON with 'text' field
    Response: Audio file (WAV format) with spoken response
    """
    request_id = generate_request_id()
    start_time = time()
    trace_id = request.headers.get('X-Trace-ID', request_id)
    
    try:
        user_id = request.form.get('user_id') or request.args.get('user_id')
        
        # Get input text (either from audio or direct text)
        if 'audio' in request.files:
            # Transcribe audio input
            audio_file = request.files['audio']
            audio_data, sample_rate = sf.read(io.BytesIO(audio_file.read()))
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            # Resample if needed
            if sample_rate != config.STT_SAMPLE_RATE:
                import librosa
                audio_data = librosa.resample(
                    audio_data,
                    orig_sr=sample_rate,
                    target_sr=config.STT_SAMPLE_RATE
                )
            
            audio_data = audio_data.astype(np.float32)
            input_text = transcribe_audio(audio_data)
            
        elif request.is_json:
            # Direct text input
            data = request.get_json()
            input_text = data.get('text', '')
        else:
            current_app.logger_instance.log_request(
                request_id=request_id,
                endpoint='/voice/speak',
                trace_id=trace_id,
                status='error',
                status_code=400,
                latency_ms=(time() - start_time) * 1000,
                error='No audio or text provided'
            )
            return APIResponse.error('No audio or text provided', request_id).to_dict(), 400
        
        if not input_text or not input_text.strip():
            current_app.logger_instance.log_request(
                request_id=request_id,
                endpoint='/voice/speak',
                trace_id=trace_id,
                status='error',
                status_code=400,
                latency_ms=(time() - start_time) * 1000,
                error='Empty input text'
            )
            return APIResponse.error('Empty input text', request_id).to_dict(), 400
        
        # Get conversation manager
        conversation = get_conversation_manager(user_id)
        
        # Send message to Chat service
        chat_response = conversation.send_message(input_text, trace_id=trace_id)
        
        # Extract response text
        chat_client = get_chat_client()
        response_text = chat_client.extract_response_text(chat_response)
        
        # Generate TTS audio
        audio = generate_audio(response_text)
        
        if len(audio) == 0:
            current_app.logger_instance.log_request(
                request_id=request_id,
                endpoint='/voice/speak',
                trace_id=trace_id,
                status='error',
                status_code=500,
                latency_ms=(time() - start_time) * 1000,
                error='Failed to generate audio response'
            )
            return APIResponse.error('Failed to generate audio response', request_id).to_dict(), 500
        
        # Convert to WAV file
        buffer = io.BytesIO()
        sf.write(buffer, audio, config.TTS_SAMPLE_RATE, format='WAV')
        buffer.seek(0)
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/voice/speak',
            trace_id=trace_id,
            status='success',
            status_code=200,
            latency_ms=latency_ms,
            result_size_bytes=buffer.getbuffer().nbytes,
            metadata={'user_id': user_id, 'input_text': input_text[:100]}
        )
        
        return send_file(
            buffer,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='response.wav'
        )
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/voice/speak',
            trace_id=trace_id,
            status='error',
            status_code=500,
            latency_ms=latency_ms,
            error=str(e)
        )
        return APIResponse.error(str(e), request_id).to_dict(), 500


@voice_bp.route('/conversation/clear', methods=['POST'])
def clear_conversation_endpoint():
    """Clear conversation history for a user."""
    request_id = generate_request_id()
    start_time = time()
    
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        clear_conversation(user_id)
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/voice/conversation/clear',
            status='success',
            status_code=200,
            latency_ms=latency_ms
        )
        
        return APIResponse.success({
            'message': 'Conversation history cleared',
            'user_id': user_id or 'anonymous'
        }, request_id).to_dict(), 200
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/voice/conversation/clear',
            status='error',
            status_code=500,
            latency_ms=latency_ms,
            error=str(e)
        )
        return APIResponse.error(str(e), request_id).to_dict(), 500
