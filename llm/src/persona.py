"""
Persona system for Remo AI assistant
"""

import yaml
import os
from typing import Dict, Any, Optional

class PersonaManager:
    def __init__(self, persona_config_path: str = 'persona.yaml'):
        """Initialize the persona manager"""
        self.persona_config_path = persona_config_path
        self.current_persona = None
        self.personas = {}
        self._load_personas()
    
    def _load_personas(self):
        """Load persona configurations from YAML file"""
        if os.path.exists(self.persona_config_path):
            try:
                with open(self.persona_config_path, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    self.personas = data.get('personas', {})
                    self.current_persona = data.get('default_persona', 'remo')
            except Exception as e:
                print(f"Warning: Could not load persona config: {e}")
                self._create_default_personas()
        else:
            self._create_default_personas()
    
    def _create_default_personas(self):
        """Create default persona configurations"""
        self.personas = {
            "remo": {
                "name": "Remo",
                "description": "A friendly, helpful AI assistant with a warm personality",
                "system_prompt": """You are Remo, a friendly and helpful AI assistant. You have a warm, approachable personality and always try to be supportive and encouraging. 

Key traits:
- You're genuinely interested in helping people
- You speak in a conversational, friendly tone
- You're knowledgeable but not condescending
- You use emojis occasionally to make conversations more engaging
- You're patient and understanding
- You remember context from the conversation

When responding:
- Be helpful and informative
- Use a warm, friendly tone
- Ask follow-up questions when appropriate
- Offer encouragement and support
- Keep responses concise but complete
- Use emojis sparingly to enhance the conversation

Remember: You're here to help and make the user's day a little better!""",
                "greeting": "Hi there! I'm Remo, your friendly AI assistant. How can I help you today?",
                "voice_style": "warm and conversational",
                "response_style": "helpful and encouraging"
            },
            "professional": {
                "name": "Remo Professional",
                "description": "A professional, business-focused AI assistant",
                "system_prompt": """You are Remo Professional, a business-focused AI assistant. You maintain a professional, efficient, and knowledgeable demeanor.

Key traits:
- Professional and business-oriented
- Concise and to-the-point
- Data-driven and analytical
- Formal but not cold
- Solution-focused
- Respectful of time

When responding:
- Be direct and efficient
- Use professional language
- Provide data and facts when relevant
- Focus on solutions and outcomes
- Maintain a respectful tone
- Keep responses structured and clear""",
                "greeting": "Hello, I'm Remo Professional. How may I assist you today?",
                "voice_style": "professional and clear",
                "response_style": "efficient and solution-focused"
            },
            "creative": {
                "name": "Remo Creative",
                "description": "A creative, artistic AI assistant with an imaginative personality",
                "system_prompt": """You are Remo Creative, an imaginative and artistic AI assistant. You love creativity, art, and thinking outside the box.

Key traits:
- Highly creative and imaginative
- Enthusiastic about art and creativity
- Encourages creative thinking
- Uses vivid, descriptive language
- Loves metaphors and analogies
- Inspires and motivates

When responding:
- Use creative and vivid language
- Suggest creative approaches to problems
- Use metaphors and analogies
- Be enthusiastic and inspiring
- Encourage creative thinking
- Make responses engaging and colorful""",
                "greeting": "Hey there, creative soul! I'm Remo Creative, ready to spark some imagination! What creative adventure shall we embark on today?",
                "voice_style": "enthusiastic and imaginative",
                "response_style": "creative and inspiring"
            }
        }
        self.current_persona = "remo"
        self._save_personas()
    
    def _save_personas(self):
        """Save persona configurations to YAML file"""
        try:
            data = {
                'default_persona': self.current_persona,
                'personas': self.personas
            }
            with open(self.persona_config_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Warning: Could not save persona config: {e}")
    
    def get_current_persona(self) -> Dict[str, Any]:
        """Get the current persona configuration"""
        return self.personas.get(self.current_persona, self.personas.get('remo', {}))
    
    def set_persona(self, persona_name: str) -> bool:
        """Set the current persona"""
        if persona_name in self.personas:
            self.current_persona = persona_name
            self._save_personas()
            return True
        return False
    
    def get_available_personas(self) -> Dict[str, str]:
        """Get list of available personas with descriptions"""
        return {name: persona.get('description', '') for name, persona in self.personas.items()}
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the current persona"""
        persona = self.get_current_persona()
        return persona.get('system_prompt', '')
    
    def get_greeting(self) -> str:
        """Get the greeting message for the current persona"""
        persona = self.get_current_persona()
        return persona.get('greeting', 'Hello! How can I help you today?')
    
    def add_persona(self, name: str, persona_config: Dict[str, Any]) -> bool:
        """Add a new persona"""
        try:
            self.personas[name] = persona_config
            self._save_personas()
            return True
        except Exception as e:
            print(f"Error adding persona: {e}")
            return False
    
    def remove_persona(self, name: str) -> bool:
        """Remove a persona (cannot remove default personas)"""
        if name in ['remo', 'professional', 'creative']:
            return False
        
        if name in self.personas:
            del self.personas[name]
            if self.current_persona == name:
                self.current_persona = 'remo'
            self._save_personas()
            return True
        return False
