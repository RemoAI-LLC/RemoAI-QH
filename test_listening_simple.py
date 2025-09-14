#!/usr/bin/env python3
"""
Simple test for the listening endpoint
"""
import requests
import json

def test_listening_endpoint():
    """Test the listening endpoint with a simple text input"""
    
    # Test data
    test_data = {
        "transcribed_text": "I have a meeting with Microsoft tomorrow about production. I need to prepare for this big tech company presentation."
    }
    
    # Test the listening endpoint
    try:
        response = requests.post(
            "http://localhost:8000/listening/process",
            data={
                "transcribed_text": test_data["transcribed_text"],
                "api_key": "A3W1B5T-1DQMWGX-P0XHR4V-7030128"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Transcribed Text: {result.get('transcribed_text')}")
            print(f"Notifications: {json.dumps(result.get('notifications', []), indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_listening_endpoint()
