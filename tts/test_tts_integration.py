#!/usr/bin/env python3
"""
Test script for TTS integration with Remo AI
Tests the complete TTS functionality including persona-specific voices
"""

import requests
import time
import json
import sys
import os
# No need to add tts to path since we're already in the tts folder

def test_tts_integration():
    """Test complete TTS integration"""
    base_url = "http://localhost:8000"
    
    print("Testing Remo AI TTS Integration")
    print("=" * 50)
    
    # Test 1: Check health with TTS
    print("\n1. Checking health with TTS service...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Health check: {data['status']}")
            print(f"[SUCCESS] Services: {data['services']}")
        else:
            print(f"[ERROR] Health check failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        return
    
    # Test 2: Check TTS status
    print("\n2. Checking TTS service status...")
    try:
        response = requests.get(f"{base_url}/tts/status")
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] TTS Status: {data['status']}")
        else:
            print(f"[ERROR] TTS status check failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error checking TTS status: {e}")
    
    # Test 3: Test persona switching with TTS
    personas = ["remo", "professional", "creative"]
    for persona in personas:
        print(f"\n3.{personas.index(persona) + 1}. Testing {persona} persona with TTS...")
        
        # Set persona
        try:
            response = requests.post(f"{base_url}/personas/{persona}")
            if response.status_code == 200:
                print(f"[SUCCESS] Switched to {persona} persona")
            else:
                print(f"[ERROR] Failed to switch to {persona} persona")
                continue
        except Exception as e:
            print(f"[ERROR] Error switching persona: {e}")
            continue
        
        # Test chat with TTS
        try:
            chat_data = {
                "message": f"Hello! I'm the {persona} persona. How can I help you today?",
                "stream": False
            }
            response = requests.post(f"{base_url}/chat", json=chat_data)
            if response.status_code == 200:
                data = response.json()
                print(f"[SUCCESS] {persona} response: {data['message'][:100]}...")
                print(f"[SUCCESS] TTS should be speaking the response now...")
                time.sleep(3)  # Wait for TTS to complete
            else:
                print(f"[ERROR] Chat failed for {persona}: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Error with {persona} chat: {e}")
    
    # Test 4: Test direct TTS functionality
    print("\n4. Testing direct TTS functionality...")
    
    # Test TTS speak
    try:
        tts_data = {
            "text": "This is a direct TTS test using the Remo persona voice.",
            "persona": "remo",
            "blocking": True
        }
        response = requests.post(f"{base_url}/tts/speak", json=tts_data)
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Direct TTS: {data['message']}")
        else:
            print(f"[ERROR] Direct TTS failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error with direct TTS: {e}")
    
    # Test TTS async
    try:
        tts_data = {
            "text": "This is an async TTS test using the professional persona.",
            "persona": "professional"
        }
        response = requests.post(f"{base_url}/tts/speak-async", json=tts_data)
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Async TTS: {data['message']}")
            print("Waiting for async speech to complete...")
            time.sleep(3)
        else:
            print(f"[ERROR] Async TTS failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error with async TTS: {e}")
    
    # Test 5: Test TTS control
    print("\n5. Testing TTS control...")
    
    # Start speech
    try:
        tts_data = {
            "text": "This is a long speech that we will interrupt in the middle.",
            "persona": "creative"
        }
        response = requests.post(f"{base_url}/tts/speak-async", json=tts_data)
        if response.status_code == 200:
            print("[SUCCESS] Started long speech...")
            time.sleep(2)  # Let it speak for a bit
            
            # Stop speech
            stop_response = requests.post(f"{base_url}/tts/stop")
            if stop_response.status_code == 200:
                print("[SUCCESS] Speech stopped successfully")
            else:
                print(f"[ERROR] Failed to stop speech: {stop_response.status_code}")
        else:
            print(f"[ERROR] Failed to start speech: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error with TTS control: {e}")
    
    # Test 6: Test TTS enable/disable
    print("\n6. Testing TTS enable/disable...")
    
    try:
        # Disable TTS
        response = requests.post(f"{base_url}/tts/disable")
        if response.status_code == 200:
            print("[SUCCESS] TTS disabled")
            
            # Try to speak (should not work)
            chat_data = {"message": "This should not be spoken.", "stream": False}
            chat_response = requests.post(f"{base_url}/chat", json=chat_data)
            if chat_response.status_code == 200:
                print("[SUCCESS] Chat worked but TTS should be disabled")
            
            # Re-enable TTS
            enable_response = requests.post(f"{base_url}/tts/enable")
            if enable_response.status_code == 200:
                print("[SUCCESS] TTS re-enabled")
            else:
                print(f"[ERROR] Failed to re-enable TTS: {enable_response.status_code}")
        else:
            print(f"[ERROR] Failed to disable TTS: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error with TTS enable/disable: {e}")
    
    print("\nTTS Integration testing completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_tts_integration()
