#!/usr/bin/env python3
"""
Test NPU directly to see if it's working
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'llm', 'src'))

from chat_client import NPUChatClient

def test_npu_direct():
    """Test NPU directly"""
    try:
        print("Initializing NPU Chat Client...")
        config_path = os.path.join(os.path.dirname(__file__), 'llm', 'config.yaml')
        chat_client = NPUChatClient(config_path)
        
        print("Testing NPU with a simple message...")
        response_generator = chat_client.send_message("Hello, how are you?", stream=False)
        if response_generator:
            response = ''.join(response_generator)
            print(f"NPU Response: {response}")
        else:
            print("No response from NPU")
        
        print("Testing NPU with notification prompt...")
        prompt = """Analyze this user conversation and generate helpful notifications or suggestions.

User said: "I have a meeting with Microsoft tomorrow about production. I need to prepare for this big tech company presentation."

Please generate 1-3 helpful notifications in this exact JSON format:
{
    "notifications": [
        {
            "title": "Notification Title",
            "preview": "Preview text (max 100 chars)",
            "fullContent": "Detailed content and suggestions",
            "action": "suggested action",
            "priority": "high|medium|low"
        }
    ]
}

Focus on:
- Meeting preparations and reminders
- Task suggestions and follow-ups
- Helpful resources and tips
- Important insights from the conversation
- Proactive assistance based on what the user mentioned

Generate practical, actionable notifications that would be helpful to the user."""
        
        response_generator = chat_client.send_message(prompt, stream=False)
        if response_generator:
            response = ''.join(response_generator)
            print(f"NPU Notification Response: {response}")
        else:
            print("No response from NPU for notification prompt")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_npu_direct()
