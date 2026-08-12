"""
Speech-to-text module using Whisper.
Refactored from original Voice/stt.py for Flask service integration.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from faster_whisper import WhisperModel
import numpy as np
import sounddevice as sd
import warnings
from io import StringIO
from Voice import config
import threading
import queue

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Global model for faster reuse
_whisper_model = None


def initialize_stt():
    """Initialize Whisper model (one-time setup)."""
    global _whisper_model
    if _whisper_model is None:
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        
        try:
            try:
                _whisper_model = WhisperModel(
                    config.STT_MODEL,
                    device="cuda",
                    compute_type="float16"
                )
            except Exception:
                _whisper_model = WhisperModel(
                    config.STT_MODEL,
                    device="cpu",
                    compute_type="int8"
                )
        finally:
            sys.stderr = old_stderr


def transcribe_audio(audio: np.ndarray) -> str:
    """
    Transcribe audio using Whisper.
    
    Args:
        audio: NumPy array of audio samples (float32, 16kHz)
        
    Returns:
        Transcribed text string
    """
    initialize_stt()
    
    if len(audio) == 0:
        return ""
    
    # faster-whisper expects float32 audio
    segments, info = _whisper_model.transcribe(
        audio,
        language="en",
        beam_size=1,
        vad_filter=True
    )
    
    # Collect all segments
    text_parts = []
    for segment in segments:
        text_parts.append(segment.text)
    
    text = " ".join(text_parts).strip()
    
    # Remove common Whisper hallucinations
    hallucinations = [
        "Thank you.",
        "Thanks for watching!",
        "Thank you for watching!",
        "Thank you for watching.",
        "Thanks for watching.",
        "Thank you!",
        "Thanks!",
        "Bye!",
        "Bye.",
        "Goodbye!",
        "Goodbye."
    ]
    
    for hallucination in hallucinations:
        if text.endswith(hallucination):
            text = text[:-len(hallucination)].strip()
            break
    
    return text


def record_audio_until_silence() -> np.ndarray:
    """
    Record audio with voice activation - start when speech detected, stop when silence detected.
    
    Returns:
        NumPy array of recorded audio samples
    """
    audio_chunks = []
    silence_counter = 0
    speech_started = False
    silence_samples = int(config.SILENCE_DURATION * config.STT_SAMPLE_RATE)
    chunk_size = int(0.1 * config.STT_SAMPLE_RATE)  # 100ms chunks
    
    def audio_callback(indata, frames, time_info, status):
        nonlocal silence_counter, speech_started
        
        audio_level = np.abs(indata).mean()
        
        # Voice activation: wait for speech to start
        if not speech_started:
            if audio_level > config.VOICE_ACTIVATION_THRESHOLD:
                speech_started = True
                audio_chunks.append(indata.copy())
                silence_counter = 0
        else:
            # Already recording, save audio
            audio_chunks.append(indata.copy())
            
            # Check if audio is silent
            if audio_level < config.SILENCE_THRESHOLD:
                silence_counter += len(indata)
            else:
                silence_counter = 0
    
    # Start listening
    with sd.InputStream(
        samplerate=config.STT_SAMPLE_RATE,
        channels=1,
        dtype='float32',
        blocksize=chunk_size,
        callback=audio_callback
    ):
        # Wait for speech to start (with timeout)
        max_wait = 60  # Maximum 60 seconds to wait for speech
        max_wait_samples = max_wait * config.STT_SAMPLE_RATE
        wait_samples = 0
        
        # Wait for voice activation
        while not speech_started and wait_samples < max_wait_samples:
            sd.sleep(100)  # Check every 100ms
            wait_samples += chunk_size
        
        if not speech_started:
            return np.array([], dtype='float32')
        
        # Record until silence or max duration
        max_recording_duration = 30  # Maximum 30 seconds of recording
        max_recording_samples = max_recording_duration * config.STT_SAMPLE_RATE
        
        while silence_counter < silence_samples:
            sd.sleep(100)  # Check every 100ms
            total_samples = sum(len(chunk) for chunk in audio_chunks)
            if total_samples >= max_recording_samples:
                break
    
    # Concatenate all chunks
    if audio_chunks:
        audio = np.concatenate(audio_chunks, axis=0)
        return audio.flatten()
    return np.array([], dtype='float32')


def listen() -> str:
    """
    Record audio and transcribe it to text.
    Convenience function combining recording and transcription.
    
    Returns:
        Transcribed text string
    """
    audio = record_audio_until_silence()
    if len(audio) == 0:
        return ""
    
    text = transcribe_audio(audio)
    return text


# ============== CONTINUOUS LISTENING SYSTEM ==============

class ContinuousListener:
    """
    Manages continuous audio listening with interruption detection.
    Always listens in the background and can detect when user starts speaking.
    """
    
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.interrupt_audio_chunks = []
        self.stream = None
        self._lock = threading.Lock()
        self.chunk_size = int(0.1 * config.STT_SAMPLE_RATE)  # 100ms chunks
        
    def start(self):
        """Start continuous listening in the background."""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.stream = sd.InputStream(
            samplerate=config.STT_SAMPLE_RATE,
            channels=1,
            dtype='float32',
            blocksize=self.chunk_size,
            callback=self._audio_callback
        )
        self.stream.start()
    
    def stop(self):
        """Stop continuous listening."""
        self.is_listening = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for continuous audio capture."""
        if self.is_listening:
            self.audio_queue.put(indata.copy())
    
    def clear_queue(self):
        """Clear the audio queue."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
    
    def check_for_voice(self, threshold=None) -> bool:
        """Check if there's voice activity above threshold."""
        if threshold is None:
            threshold = config.VOICE_ACTIVATION_THRESHOLD
        
        try:
            chunk = self.audio_queue.get_nowait()
            audio_level = np.abs(chunk).mean()
            return audio_level > threshold
        except queue.Empty:
            return False
    
    def wait_for_voice_and_record(self, initial_audio: list = None) -> np.ndarray:
        """
        Wait for voice activation then record until silence.
        
        Args:
            initial_audio: Optional list of audio chunks to use as start
            
        Returns:
            NumPy array of recorded audio
        """
        audio_chunks = initial_audio if initial_audio else []
        silence_counter = 0
        speech_started = len(audio_chunks) > 0
        silence_samples = int(config.SILENCE_DURATION * config.STT_SAMPLE_RATE)
        
        # Clear old audio from queue if starting fresh
        if not speech_started:
            self.clear_queue()
        
        max_wait = 60 * config.STT_SAMPLE_RATE
        max_recording = 30 * config.STT_SAMPLE_RATE
        waited = 0
        
        while self.is_listening:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
                audio_level = np.abs(chunk).mean()
                
                if not speech_started:
                    waited += len(chunk)
                    if waited > max_wait:
                        return np.array([], dtype='float32')
                    
                    if audio_level > config.VOICE_ACTIVATION_THRESHOLD:
                        speech_started = True
                        audio_chunks.append(chunk)
                        silence_counter = 0
                else:
                    audio_chunks.append(chunk)
                    
                    if audio_level < config.SILENCE_THRESHOLD:
                        silence_counter += len(chunk)
                    else:
                        silence_counter = 0
                    
                    # Check for end conditions
                    total_samples = sum(len(c) for c in audio_chunks)
                    if silence_counter >= silence_samples or total_samples >= max_recording:
                        break
                        
            except queue.Empty:
                continue
        
        if audio_chunks:
            audio = np.concatenate(audio_chunks, axis=0)
            return audio.flatten()
        return np.array([], dtype='float32')
    
    def get_interruption_audio(self) -> list:
        """Get any audio chunks captured during an interruption."""
        with self._lock:
            audio = self.interrupt_audio_chunks.copy()
            self.interrupt_audio_chunks = []
            return audio
    
    def set_interruption_audio(self, chunks: list):
        """Store audio chunks from an interruption."""
        with self._lock:
            self.interrupt_audio_chunks = chunks


# Global continuous listener instance
_continuous_listener = None


def get_continuous_listener() -> ContinuousListener:
    """Get or create the global continuous listener."""
    global _continuous_listener
    if _continuous_listener is None:
        _continuous_listener = ContinuousListener()
    return _continuous_listener


def listen_continuous(initial_audio: list = None) -> str:
    """
    Listen using continuous listener and transcribe.
    
    Args:
        initial_audio: Optional list of audio chunks from interruption
        
    Returns:
        Transcribed text string
    """
    listener = get_continuous_listener()
    audio = listener.wait_for_voice_and_record(initial_audio)
    
    if len(audio) == 0:
        return ""
    
    text = transcribe_audio(audio)
    return text
