"""
Chat client for AnythingLLM API with NPU acceleration
"""
import requests
import yaml
import json
import sys
from typing import Dict, Any, Generator, Optional

class NPUChatClient:
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the chat client with configuration"""
        self.config = self._load_config(config_path)
        self.headers = {
            'Authorization': f"Bearer {self.config['api_key']}",
            'Content-Type': 'application/json'
        }
        self.conversation_history = []
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: {config_path} not found. Please create it with your API key and settings.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing {config_path}: {e}")
            sys.exit(1)
    
    def send_message(self, message: str, stream: bool = None) -> Optional[Generator[str, None, None]]:
        """Send a message to the AnythingLLM API"""
        if stream is None:
            stream = self.config.get('stream', True)
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        payload = {
            "message": message,
            "workspaceSlug": self.config['workspace_slug'],
            "mode": "chat",
            "stream": stream
        }
        
        try:
            if stream:
                return self._stream_response(payload)
            else:
                return self._get_complete_response(payload)
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
            return None
    
    def _stream_response(self, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """Stream response from AnythingLLM API"""
        try:
            response = requests.post(
                f"{self.config['model_server_base_url']}/workspace/{self.config['workspace_slug']}/chat",
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=self.config.get('stream_timeout', 60)
            )
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                return
            
            # Process streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    # Handle different streaming formats
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            if 'text' in data:
                                chunk = data['text']
                                full_response += chunk
                                yield chunk
                            elif 'textResponse' in data:
                                chunk = data['textResponse']
                                full_response += chunk
                                yield chunk
                            elif 'error' in data:
                                print(f"Error in stream: {data['error']}")
                                break
                        except json.JSONDecodeError:
                            continue
                    elif line_str.strip():  # Handle non-SSE format
                        try:
                            data = json.loads(line_str)
                            if 'textResponse' in data:
                                # Simulate streaming by yielding the response character by character
                                text_response = data['textResponse']
                                full_response = text_response
                                for char in text_response:
                                    yield char
                                break  # Exit after processing the complete response
                            elif 'text' in data:
                                text_response = data['text']
                                full_response = text_response
                                for char in text_response:
                                    yield char
                                break
                        except json.JSONDecodeError:
                            continue
            
            # Add assistant response to conversation history
            if full_response:
                self.conversation_history.append({"role": "assistant", "content": full_response})
                
        except Exception as e:
            print(f"Streaming error: {e}")
            return
    
    def _get_complete_response(self, payload: Dict[str, Any]) -> Optional[str]:
        """Get complete response from AnythingLLM API"""
        try:
            response = requests.post(
                f"{self.config['model_server_base_url']}/workspace/{self.config['workspace_slug']}/chat",
                headers=self.headers,
                json=payload,
                timeout=self.config.get('stream_timeout', 60)
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'textResponse' in data:
                    assistant_message = data['textResponse']
                    self.conversation_history.append({"role": "assistant", "content": assistant_message})
                    return assistant_message
                else:
                    print(f"Unexpected response format: {data}")
                    return None
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self) -> list:
        """Get conversation history"""
        return self.conversation_history.copy()
