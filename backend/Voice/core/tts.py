"""
Text-to-speech module using Kokoro TTS.
Refactored from original Voice/tts.py for Flask service integration.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import re
import numpy as np
import torch
import sounddevice as sd
from kokoro import KPipeline
from Voice import config
import warnings

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
os.environ["TRANSFORMERS_NO_TORCHVISION"] = "1"

# Global pipeline and voice for faster reuse
_tts_pipeline = None
_tts_voice = None


def clean_text_for_tts(text: str) -> str:
    """
    Remove all markdown symbols and emojis for TTS.
    
    Args:
        text: Raw text with potential markdown/emojis
        
    Returns:
        Cleaned text suitable for TTS
    """
    # Remove emojis and non-BMP symbols
    text = re.sub(r"[\U00010000-\U0010ffff]", "", text)
    # Remove common emojis in BMP range
    text = re.sub(r"[\u2600-\u26FF\u2700-\u27BF\u1F300-\u1F5FF\u1F600-\u1F64F\u1F680-\u1F6FF\u1F900-\u1F9FF]", "", text)
    
    # Remove markdown formatting
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # Bold **text**
    text = re.sub(r"\*([^*]+)\*", r"\1", text)      # Italic *text*
    text = re.sub(r"__([^_]+)__", r"\1", text)      # Bold __text__
    text = re.sub(r"_([^_]+)_", r"\1", text)        # Italic _text_
    text = re.sub(r"~~([^~]+)~~", r"\1", text)      # Strikethrough ~~text~~
    text = re.sub(r"`([^`]+)`", r"\1", text)        # Inline code `text`
    text = re.sub(r"```[\s\S]*?```", "", text)      # Code blocks
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)  # Headers
    text = re.sub(r"^[*\-+]\s+", "", text, flags=re.MULTILINE)  # Bullet lists
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)  # Numbered lists
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # Links [text](url)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)  # Images ![alt](url)
    text = re.sub(r"^>+\s*", "", text, flags=re.MULTILINE)  # Blockquotes
    text = re.sub(r"---+", "", text)  # Horizontal rules
    
    return text.strip()


def initialize_tts():
    """Initialize TTS pipeline and voice (one-time setup)."""
    global _tts_pipeline, _tts_voice
    if _tts_pipeline is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Use local model directory if it exists
        local_dir = os.path.join(os.path.dirname(__file__), "..", "models", "kokoro")
        repo_id = local_dir if os.path.exists(local_dir) else config.TTS_REPO_ID
        
        _tts_pipeline = KPipeline(
            lang_code=config.TTS_LANG_CODE,
            repo_id=repo_id
        ).to(device)
        
        _tts_voice = torch.load(config.TTS_VOICE_PATH, map_location=device)


def generate_audio(text: str) -> np.ndarray:
    """
    Generate audio from text using Kokoro TTS.
    
    Args:
        text: Text to convert to speech
        
    Returns:
        NumPy array of audio samples (float32)
    """
    if not text:
        return np.array([], dtype=np.float32)
    
    initialize_tts()
    
    # Clean text for TTS
    clean = clean_text_for_tts(text)
    if not clean:
        return np.array([], dtype=np.float32)
    
    # Generate audio chunks
    chunks: list[np.ndarray] = []
    for _, _, audio in _tts_pipeline(clean, voice=_tts_voice, speed=config.TTS_SPEED):
        if isinstance(audio, torch.Tensor):
            a = audio.detach().cpu().numpy().astype(np.float32)
        else:
            a = np.asarray(audio, dtype=np.float32)
        chunks.append(a)
    
    if chunks:
        return np.concatenate(chunks)
    return np.array([], dtype=np.float32)


def play_audio(audio: np.ndarray):
    """
    Play audio using sounddevice (blocking).
    
    Args:
        audio: NumPy array of audio samples
    """
    if len(audio) == 0:
        return
    
    sd.play(audio, config.TTS_SAMPLE_RATE, blocking=True)
    sd.stop()


def text_to_speech(text: str) -> float:
    """
    Convert text to speech and play it.
    Convenience function combining generation and playback.
    
    Args:
        text: Text to speak
        
    Returns:
        Duration in seconds
    """
    audio = generate_audio(text)
    if len(audio) == 0:
        return 0.0
    
    play_audio(audio)
    return len(audio) / config.TTS_SAMPLE_RATE


def play_tts_interruptible(text: str) -> tuple[float, bool, list]:
    """
    Generate and play TTS audio with interruption detection.
    Monitors microphone during playback and stops if user starts speaking.
    
    Args:
        text: Text to speak
        
    Returns:
        Tuple of (duration, was_interrupted, interruption_audio_chunks)
    """
    if not text:
        return 0.0, False, []
    
    # Generate audio first
    audio = generate_audio(text)
    if len(audio) == 0:
        return 0.0, False, []
    
    total_duration = len(audio) / config.TTS_SAMPLE_RATE
    
    # Variables for interruption detection
    was_interrupted = False
    interruption_chunks = []
    chunk_size = int(0.05 * config.STT_SAMPLE_RATE)  # 50ms chunks
    
    # Callback to monitor microphone during playback
    def mic_callback(indata, frames, time_info, status):
        nonlocal was_interrupted, interruption_chunks
        if not was_interrupted:
            audio_level = np.abs(indata).mean()
            if audio_level > config.INTERRUPTION_THRESHOLD:
                was_interrupted = True
                sd.stop()  # Stop TTS playback immediately
        
        # Capture user's speech if interrupted
        if was_interrupted:
            interruption_chunks.append(indata.copy())
    
    # Start microphone monitoring
    mic_stream = sd.InputStream(
        samplerate=config.STT_SAMPLE_RATE,
        channels=1,
        dtype='float32',
        blocksize=chunk_size,
        callback=mic_callback
    )
    
    try:
        mic_stream.start()
        
        # Play TTS audio (may be interrupted)
        sd.play(audio, config.TTS_SAMPLE_RATE)
        sd.wait()
        
    finally:
        mic_stream.stop()
        mic_stream.close()
    
    return total_duration, was_interrupted, interruption_chunks
