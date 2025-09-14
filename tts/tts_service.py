"""
Text-to-Speech Service using eSpeak
Provides voice synthesis for Remo AI responses
"""

import subprocess
import tempfile
import os
import threading
import time
import logging
from typing import Optional, Callable
import platform

# Import Windows SAPI fallback
try:
    from windows_tts import WindowsTTSService
except ImportError:
    WindowsTTSService = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, voice: str = "en", speed: int = 175, pitch: int = 50, volume: int = 100):
        """
        Initialize TTS service with eSpeak
        
        Args:
            voice: Voice language/accent (e.g., 'en', 'en-us', 'en-gb')
            speed: Speech rate in words per minute (default: 175)
            pitch: Voice pitch (0-99, default: 50)
            volume: Voice volume (0-200, default: 100)
        """
        self.voice = voice
        self.speed = speed
        self.pitch = pitch
        self.volume = volume
        self.is_speaking = False
        self.current_process = None
        self.supported_voices = []
        
        # Initialize Windows SAPI fallback
        self.windows_tts = None
        
        # Check if eSpeak is installed
        self.espeak_available = self._check_espeak()
        if not self.espeak_available:
            logger.warning("eSpeak not found. Trying Windows SAPI fallback...")
            # Try Windows SAPI as fallback
            if platform.system() == "Windows" and WindowsTTSService:
                try:
                    self.windows_tts = WindowsTTSService()
                    if self.windows_tts.available:
                        logger.info("Using Windows SAPI as TTS fallback")
                        self.espeak_available = True  # Mark as available for compatibility
                    else:
                        logger.warning("Windows SAPI also not available")
                        self.windows_tts = None
                except Exception as e:
                    logger.warning(f"Failed to initialize Windows SAPI: {e}")
                    self.windows_tts = None
            else:
                logger.warning("TTS functionality will be limited.")
        else:
            self._load_supported_voices()
    
    def _check_espeak(self) -> bool:
        """Check if eSpeak is installed and available"""
        try:
            result = subprocess.run(['espeak', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"eSpeak found: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        
        # Try alternative commands for different systems
        alternatives = ['espeak-ng', 'espeak-ng.exe', 'espeak.exe']
        for cmd in alternatives:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info(f"eSpeak found as '{cmd}': {result.stdout.strip()}")
                    self.espeak_cmd = cmd
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        logger.error("eSpeak not found. Please install eSpeak or eSpeak-ng")
        return False
    
    def _load_supported_voices(self):
        """Load list of supported voices"""
        try:
            result = subprocess.run([self.espeak_cmd, '--voices'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                self.supported_voices = []
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 4:
                        voice_code = parts[1]
                        voice_name = ' '.join(parts[3:])
                        self.supported_voices.append({
                            'code': voice_code,
                            'name': voice_name
                        })
                logger.info(f"Loaded {len(self.supported_voices)} supported voices")
        except Exception as e:
            logger.warning(f"Could not load voice list: {e}")
            self.supported_voices = []
    
    def speak(self, text: str, blocking: bool = False) -> bool:
        """
        Speak the given text
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
            
        Returns:
            True if speech started successfully, False otherwise
        """
        if not self.espeak_available:
            logger.error("TTS not available")
            return False
        
        if not text.strip():
            logger.warning("Empty text provided for speech")
            return False
        
        # Use Windows SAPI if eSpeak is not available
        if hasattr(self, 'windows_tts') and self.windows_tts:
            return self.windows_tts.speak(text, blocking)
        
        # Stop any current speech
        self.stop_speaking()
        
        try:
            # Prepare eSpeak command
            cmd = [
                self.espeak_cmd,
                '-v', self.voice,
                '-s', str(self.speed),
                '-p', str(self.pitch),
                '-a', str(self.volume),
                '--stdout'  # Output to stdout for better control
            ]
            
            # Start speaking process
            self.is_speaking = True
            self.current_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send text to eSpeak
            stdout, stderr = self.current_process.communicate(input=text)
            
            if self.current_process.returncode == 0:
                logger.info(f"Spoke: {text[:50]}...")
                if blocking:
                    self.is_speaking = False
                return True
            else:
                logger.error(f"eSpeak error: {stderr}")
                self.is_speaking = False
                return False
                
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            self.is_speaking = False
            return False
    
    def speak_async(self, text: str, callback: Optional[Callable] = None) -> bool:
        """
        Speak text asynchronously
        
        Args:
            text: Text to speak
            callback: Optional callback function to call when done
            
        Returns:
            True if speech started successfully, False otherwise
        """
        # Use Windows SAPI if available
        if hasattr(self, 'windows_tts') and self.windows_tts:
            return self.windows_tts.speak_async(text, callback)
        
        def speak_thread():
            success = self.speak(text, blocking=True)
            if callback:
                callback(success, text)
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
        return True
    
    def speak_to_file(self, text: str, filename: str) -> bool:
        """
        Convert text to speech and save to audio file
        
        Args:
            text: Text to convert
            filename: Output audio file path
            
        Returns:
            True if successful, False otherwise
        """
        if not self.espeak_available:
            logger.error("eSpeak not available")
            return False
        
        try:
            cmd = [
                self.espeak_cmd,
                '-v', self.voice,
                '-s', str(self.speed),
                '-p', str(self.pitch),
                '-a', str(self.volume),
                '-w', filename,  # Write to file
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Saved speech to: {filename}")
                return True
            else:
                logger.error(f"eSpeak file error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating speech file: {e}")
            return False
    
    def stop_speaking(self):
        """Stop current speech"""
        # Use Windows SAPI if available
        if hasattr(self, 'windows_tts') and self.windows_tts:
            self.windows_tts.stop_speaking()
            return
        
        if self.current_process and self.is_speaking:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
            except Exception as e:
                logger.warning(f"Error stopping speech: {e}")
            finally:
                self.current_process = None
                self.is_speaking = False
    
    def set_voice(self, voice: str) -> bool:
        """
        Set the voice for speech
        
        Args:
            voice: Voice code (e.g., 'en', 'en-us', 'en-gb')
            
        Returns:
            True if voice is valid, False otherwise
        """
        if not self.supported_voices:
            # If we can't load voices, accept any voice
            self.voice = voice
            return True
        
        # Check if voice is supported
        for v in self.supported_voices:
            if v['code'] == voice:
                self.voice = voice
                logger.info(f"Voice set to: {voice}")
                return True
        
        logger.warning(f"Voice '{voice}' not found in supported voices")
        return False
    
    def set_speed(self, speed: int):
        """Set speech speed (words per minute)"""
        self.speed = max(80, min(500, speed))  # Clamp between 80-500
        logger.info(f"Speed set to: {self.speed} WPM")
    
    def set_pitch(self, pitch: int):
        """Set voice pitch (0-99)"""
        self.pitch = max(0, min(99, pitch))  # Clamp between 0-99
        logger.info(f"Pitch set to: {self.pitch}")
    
    def set_volume(self, volume: int):
        """Set voice volume (0-200)"""
        self.volume = max(0, min(200, volume))  # Clamp between 0-200
        logger.info(f"Volume set to: {self.volume}")
    
    def get_status(self) -> dict:
        """Get current TTS service status"""
        # Use Windows SAPI status if available
        if hasattr(self, 'windows_tts') and self.windows_tts:
            return self.windows_tts.get_status()
        
        return {
            'available': self.espeak_available,
            'speaking': self.is_speaking,
            'voice': self.voice,
            'speed': self.speed,
            'pitch': self.pitch,
            'volume': self.volume,
            'supported_voices': len(self.supported_voices),
            'type': 'eSpeak'
        }
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_speaking()
