"""
Windows SAPI TTS Service as fallback for eSpeak
Uses Windows built-in Speech API when eSpeak is not available
"""

import subprocess
import threading
import logging
from typing import Optional, Callable

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WindowsTTSService:
    def __init__(self, voice: str = "Microsoft David Desktop", speed: int = 0, pitch: int = 0, volume: int = 100):
        """
        Initialize Windows SAPI TTS service
        
        Args:
            voice: Voice name (e.g., 'Microsoft David Desktop', 'Microsoft Zira Desktop')
            speed: Speech rate (-10 to 10, default: 0)
            pitch: Voice pitch (-10 to 10, default: 0)
            volume: Voice volume (0 to 100, default: 100)
        """
        self.voice = voice
        self.speed = speed
        self.pitch = pitch
        self.volume = volume
        self.is_speaking = False
        self.current_process = None
        self.available = self._check_windows_tts()
        
        if self.available:
            logger.info("Windows SAPI TTS service initialized successfully")
        else:
            logger.warning("Windows SAPI TTS not available")
    
    def _check_windows_tts(self) -> bool:
        """Check if Windows SAPI TTS is available"""
        try:
            # Test with a simple PowerShell command
            result = subprocess.run([
                'powershell', '-Command', 
                'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Dispose()'
            ], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Windows SAPI TTS check failed: {e}")
            return False
    
    def speak(self, text: str, blocking: bool = False) -> bool:
        """
        Speak the given text using Windows SAPI
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
            
        Returns:
            True if speech started successfully, False otherwise
        """
        if not self.available:
            logger.error("Windows SAPI TTS not available")
            return False
        
        if not text.strip():
            logger.warning("Empty text provided for speech")
            return False
        
        # Stop any current speech
        self.stop_speaking()
        
        try:
            # Clean text for better speech
            cleaned_text = self._clean_text_for_speech(text)
            
            # Create PowerShell command for SAPI
            ps_command = f'''
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.SelectVoice("{self.voice}")
            $synth.Rate = {self.speed}
            $synth.Volume = {self.volume}
            $synth.Speak("{cleaned_text}")
            $synth.Dispose()
            '''
            
            # Start speaking process
            self.is_speaking = True
            self.current_process = subprocess.Popen([
                'powershell', '-Command', ps_command
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if blocking:
                # Wait for completion
                stdout, stderr = self.current_process.communicate()
                self.is_speaking = False
                
                if self.current_process.returncode == 0:
                    logger.info(f"Spoke: {text[:50]}...")
                    return True
                else:
                    logger.error(f"Windows SAPI error: {stderr}")
                    return False
            else:
                # Non-blocking
                logger.info(f"Started speaking: {text[:50]}...")
                return True
                
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
        def speak_thread():
            success = self.speak(text, blocking=True)
            if callback:
                callback(success, text)
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
        return True
    
    def _clean_text_for_speech(self, text: str) -> str:
        """
        Clean text to make it more suitable for speech synthesis
        
        Args:
            text: Original text
            
        Returns:
            Cleaned text
        """
        import re
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove URLs
        text = re.sub(r'https?://([^\s]+)', r'\1', text)
        
        # Replace common symbols with words
        replacements = {
            '&': 'and',
            '@': 'at',
            '#': 'hash',
            '%': 'percent',
            '$': 'dollar',
            '+': 'plus',
            '=': 'equals',
            '<': 'less than',
            '>': 'greater than',
            '|': 'pipe',
            '\\': 'backslash',
            '/': 'slash',
            '~': 'tilde',
            '^': 'caret',
            '`': 'backtick',
            '[': 'left bracket',
            ']': 'right bracket',
            '{': 'left brace',
            '}': 'right brace',
            '(': 'left parenthesis',
            ')': 'right parenthesis',
        }
        
        for symbol, word in replacements.items():
            text = text.replace(symbol, f' {word} ')
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Escape quotes for PowerShell
        text = text.replace('"', '""')
        
        return text.strip()
    
    def stop_speaking(self):
        """Stop current speech"""
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
            voice: Voice name
            
        Returns:
            True if voice is valid, False otherwise
        """
        self.voice = voice
        logger.info(f"Voice set to: {voice}")
        return True
    
    def set_speed(self, speed: int):
        """Set speech speed (-10 to 10)"""
        self.speed = max(-10, min(10, speed))
        logger.info(f"Speed set to: {self.speed}")
    
    def set_pitch(self, pitch: int):
        """Set voice pitch (-10 to 10)"""
        self.pitch = max(-10, min(10, pitch))
        logger.info(f"Pitch set to: {self.pitch}")
    
    def set_volume(self, volume: int):
        """Set voice volume (0 to 100)"""
        self.volume = max(0, min(100, volume))
        logger.info(f"Volume set to: {self.volume}")
    
    def get_status(self) -> dict:
        """Get current TTS service status"""
        return {
            'available': self.available,
            'speaking': self.is_speaking,
            'voice': self.voice,
            'speed': self.speed,
            'pitch': self.pitch,
            'volume': self.volume,
            'type': 'Windows SAPI'
        }
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_speaking()
