"""
Audio utility functions for Whisper integration
"""

import wave
import pyaudio
import numpy as np
import base64
import io
from typing import Tuple, Optional

def convert_audio_to_wav(audio_data: bytes, sample_rate: int = 16000, 
                        channels: int = 1, sample_width: int = 2) -> bytes:
    """
    Convert raw audio data to WAV format.
    
    Args:
        audio_data: Raw audio data
        sample_rate: Sample rate (default: 16000)
        channels: Number of channels (default: 1 for mono)
        sample_width: Sample width in bytes (default: 2 for 16-bit)
    
    Returns:
        WAV formatted audio data
    """
    wav_buffer = io.BytesIO()
    
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)
    
    wav_buffer.seek(0)
    return wav_buffer.getvalue()

def convert_wav_to_base64(wav_data: bytes) -> str:
    """
    Convert WAV data to base64 string.
    
    Args:
        wav_data: WAV formatted audio data
    
    Returns:
        Base64 encoded string
    """
    return base64.b64encode(wav_data).decode('utf-8')

def convert_base64_to_wav(base64_data: str) -> bytes:
    """
    Convert base64 string to WAV data.
    
    Args:
        base64_data: Base64 encoded audio data
    
    Returns:
        WAV formatted audio data
    """
    return base64.b64decode(base64_data)

def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
    """
    Normalize audio data to prevent clipping.
    
    Args:
        audio_data: Audio data as numpy array
    
    Returns:
        Normalized audio data
    """
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        return audio_data / max_val * 0.95  # Leave some headroom
    return audio_data

def resample_audio(audio_data: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
    """
    Resample audio data to target sample rate.
    
    Args:
        audio_data: Audio data as numpy array
        original_rate: Original sample rate
        target_rate: Target sample rate
    
    Returns:
        Resampled audio data
    """
    if original_rate == target_rate:
        return audio_data
    
    # Simple linear interpolation resampling
    ratio = target_rate / original_rate
    new_length = int(len(audio_data) * ratio)
    
    # Create new time indices
    old_indices = np.linspace(0, len(audio_data) - 1, len(audio_data))
    new_indices = np.linspace(0, len(audio_data) - 1, new_length)
    
    # Interpolate
    resampled = np.interp(new_indices, old_indices, audio_data)
    
    return resampled.astype(audio_data.dtype)

def get_audio_info(wav_data: bytes) -> Tuple[int, int, int, int]:
    """
    Get audio information from WAV data.
    
    Args:
        wav_data: WAV formatted audio data
    
    Returns:
        Tuple of (sample_rate, channels, sample_width, frames)
    """
    wav_buffer = io.BytesIO(wav_data)
    
    with wave.open(wav_buffer, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frames = wav_file.getnframes()
    
    return sample_rate, channels, sample_width, frames

def validate_audio_format(sample_rate: int, channels: int, sample_width: int) -> bool:
    """
    Validate audio format for Whisper.
    
    Args:
        sample_rate: Sample rate
        channels: Number of channels
        sample_width: Sample width in bytes
    
    Returns:
        True if format is valid for Whisper
    """
    # Whisper works best with 16kHz mono audio
    return (sample_rate >= 8000 and sample_rate <= 48000 and 
            channels == 1 and sample_width == 2)
