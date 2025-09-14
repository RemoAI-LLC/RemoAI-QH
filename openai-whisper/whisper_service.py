"""
OpenAI Whisper Service for Speech-to-Text Conversion
"""

import whisper
import tempfile
import os
import wave
import pyaudio
import threading
import time
from typing import Optional, Callable
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper service with specified model size.
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self.model_size = model_size
        self.model = None
        self.is_recording = False
        self.audio_frames = []
        self.audio = None
        self.stream = None
        
    def load_model(self):
        """Load the Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_audio_file(self, audio_file_path: str) -> str:
        """
        Transcribe audio from a file.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        if self.model is None:
            self.load_model()
        
        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")
            result = self.model.transcribe(audio_file_path)
            transcribed_text = result["text"].strip()
            logger.info(f"Transcription completed: {transcribed_text[:50]}...")
            return transcribed_text
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            raise
    
    def transcribe_audio_data(self, audio_data: bytes) -> str:
        """
        Transcribe audio from raw audio data.
        
        Args:
            audio_data: Raw audio data as bytes
            
        Returns:
            Transcribed text
        """
        if self.model is None:
            self.load_model()
        
        try:
            # Create a temporary file for the audio data
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Transcribe the temporary file
            result = self.model.transcribe(temp_file_path)
            transcribed_text = result["text"].strip()
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            logger.info(f"Transcription completed: {transcribed_text[:50]}...")
            return transcribed_text
        except Exception as e:
            logger.error(f"Failed to transcribe audio data: {e}")
            raise
    
    def start_recording(self, sample_rate: int = 16000, chunk_size: int = 1024):
        """
        Start recording audio from microphone.
        
        Args:
            sample_rate: Audio sample rate
            chunk_size: Audio chunk size
        """
        if self.is_recording:
            logger.warning("Already recording")
            return
        
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk_size
            )
            
            self.audio_frames = []
            self.is_recording = True
            
            logger.info("Started recording")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            raise
    
    def stop_recording(self) -> bytes:
        """
        Stop recording and return audio data.
        
        Returns:
            Audio data as bytes
        """
        if not self.is_recording:
            logger.warning("Not currently recording")
            return b""
        
        try:
            self.is_recording = False
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            if self.audio:
                self.audio.terminate()
                self.audio = None
            
            # Convert frames to audio data
            audio_data = b''.join(self.audio_frames)
            self.audio_frames = []
            
            logger.info("Stopped recording")
            return audio_data
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            raise
    
    def record_audio(self, duration: float = 5.0, sample_rate: int = 16000, chunk_size: int = 1024) -> bytes:
        """
        Record audio for a specified duration.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Audio sample rate
            chunk_size: Audio chunk size
            
        Returns:
            Audio data as bytes
        """
        self.start_recording(sample_rate, chunk_size)
        
        try:
            # Record for the specified duration
            for _ in range(int(sample_rate / chunk_size * duration)):
                if not self.is_recording:
                    break
                data = self.stream.read(chunk_size)
                self.audio_frames.append(data)
        except Exception as e:
            logger.error(f"Error during recording: {e}")
            raise
        finally:
            return self.stop_recording()
    
    def record_audio_with_callback(self, callback: Callable[[bytes], None], 
                                 sample_rate: int = 16000, chunk_size: int = 1024):
        """
        Record audio continuously and call callback with audio data.
        
        Args:
            callback: Function to call with audio data
            sample_rate: Audio sample rate
            chunk_size: Audio chunk size
        """
        def record_thread():
            self.start_recording(sample_rate, chunk_size)
            
            try:
                while self.is_recording:
                    data = self.stream.read(chunk_size)
                    self.audio_frames.append(data)
                    callback(data)
            except Exception as e:
                logger.error(f"Error during continuous recording: {e}")
            finally:
                self.stop_recording()
        
        thread = threading.Thread(target=record_thread)
        thread.daemon = True
        thread.start()
    
    def cleanup(self):
        """Clean up resources."""
        if self.is_recording:
            self.stop_recording()
        
        if self.stream:
            self.stream.close()
            self.stream = None
        
        if self.audio:
            self.audio.terminate()
            self.audio = None
