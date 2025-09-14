"""
Persona-specific Text-to-Speech Manager
Adapts voice characteristics based on AI persona
"""

import logging
from typing import Dict, Any, Optional
from tts_service import TTSService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonaTTSManager:
    def __init__(self):
        """Initialize persona-specific TTS manager"""
        self.tts_service = TTSService()
        self.persona_voices = self._setup_persona_voices()
        self.current_persona = None
        self.enabled = True
    
    def _setup_persona_voices(self) -> Dict[str, Dict[str, Any]]:
        """Setup voice characteristics for each persona"""
        return {
            "remo": {
                "voice": "en",
                "speed": 180,  # Friendly and conversational
                "pitch": 55,   # Slightly higher pitch for warmth
                "volume": 100,
                "description": "Warm and friendly voice"
            },
            "professional": {
                "voice": "en-us",
                "speed": 160,  # Slower, more deliberate
                "pitch": 45,   # Lower, more authoritative
                "volume": 95,
                "description": "Professional and authoritative voice"
            },
            "creative": {
                "voice": "en-gb",
                "speed": 200,  # Faster, more energetic
                "pitch": 60,   # Higher pitch for enthusiasm
                "volume": 105,
                "description": "Energetic and creative voice"
            }
        }
    
    def set_persona(self, persona_name: str) -> bool:
        """
        Set voice characteristics for the specified persona
        
        Args:
            persona_name: Name of the persona ('remo', 'professional', 'creative')
            
        Returns:
            True if persona was set successfully, False otherwise
        """
        if persona_name not in self.persona_voices:
            logger.warning(f"Unknown persona: {persona_name}")
            return False
        
        voice_config = self.persona_voices[persona_name]
        
        # Apply voice settings
        self.tts_service.set_voice(voice_config["voice"])
        self.tts_service.set_speed(voice_config["speed"])
        self.tts_service.set_pitch(voice_config["pitch"])
        self.tts_service.set_volume(voice_config["volume"])
        
        self.current_persona = persona_name
        logger.info(f"TTS voice set for persona '{persona_name}': {voice_config['description']}")
        return True
    
    def speak_persona_response(self, text: str, persona_name: str = None, blocking: bool = False) -> bool:
        """
        Speak text using the appropriate persona voice
        
        Args:
            text: Text to speak
            persona_name: Persona to use (if None, uses current persona)
            blocking: If True, wait for speech to complete
            
        Returns:
            True if speech started successfully, False otherwise
        """
        if not self.enabled:
            logger.info("TTS is disabled")
            return False
        
        if not text.strip():
            logger.warning("Empty text provided for speech")
            return False
        
        # Use specified persona or current persona
        target_persona = persona_name or self.current_persona
        if target_persona and target_persona != self.current_persona:
            self.set_persona(target_persona)
        
        # Clean text for better speech
        cleaned_text = self._clean_text_for_speech(text)
        
        # Speak the text
        return self.tts_service.speak(cleaned_text, blocking)
    
    def speak_persona_response_async(self, text: str, persona_name: str = None, 
                                   callback: Optional[callable] = None) -> bool:
        """
        Speak text asynchronously using persona voice
        
        Args:
            text: Text to speak
            persona_name: Persona to use
            callback: Optional callback function
            
        Returns:
            True if speech started successfully, False otherwise
        """
        if not self.enabled:
            logger.info("TTS is disabled")
            return False
        
        def speak_thread():
            success = self.speak_persona_response(text, persona_name, blocking=True)
            if callback:
                callback(success, text, persona_name)
        
        import threading
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
        # Remove markdown formatting
        import re
        
        # Remove markdown bold/italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove markdown code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove URLs (keep domain for speech)
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
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    def enable(self):
        """Enable TTS functionality"""
        self.enabled = True
        logger.info("TTS enabled")
    
    def disable(self):
        """Disable TTS functionality"""
        self.enabled = False
        self.tts_service.stop_speaking()
        logger.info("TTS disabled")
    
    def stop_speaking(self):
        """Stop current speech"""
        self.tts_service.stop_speaking()
    
    def get_status(self) -> Dict[str, Any]:
        """Get TTS service status"""
        status = self.tts_service.get_status()
        status.update({
            'enabled': self.enabled,
            'current_persona': self.current_persona,
            'persona_voices': list(self.persona_voices.keys())
        })
        return status
    
    def add_custom_persona_voice(self, persona_name: str, voice_config: Dict[str, Any]) -> bool:
        """
        Add custom voice configuration for a persona
        
        Args:
            persona_name: Name of the persona
            voice_config: Voice configuration dict
            
        Returns:
            True if added successfully, False otherwise
        """
        required_keys = ['voice', 'speed', 'pitch', 'volume', 'description']
        if not all(key in voice_config for key in required_keys):
            logger.error(f"Invalid voice config. Required keys: {required_keys}")
            return False
        
        self.persona_voices[persona_name] = voice_config
        logger.info(f"Added custom voice for persona '{persona_name}'")
        return True
    
    def cleanup(self):
        """Clean up resources"""
        self.tts_service.cleanup()
