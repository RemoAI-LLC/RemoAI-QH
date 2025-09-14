#!/usr/bin/env python3
"""
Test script for TTS functionality
"""

import requests
import time
import json

def test_tts_endpoints():
    """Test all TTS API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Remo AI TTS System")
    print("=" * 50)
    
    # Test 1: Get TTS status
    print("\n1. Getting TTS status...")
    try:
        response = requests.get(f"{base_url}/tts/status")
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] TTS Status: {data['status']}")
        else:
            print(f"[ERROR] Status check failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        return
    
    # Test 2: Get available voices
    print("\n2. Getting available voices...")
    try:
        response = requests.get(f"{base_url}/tts/voices")
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Found {len(data['espeak_voices'])} eSpeak voices")
            print(f"[SUCCESS] Persona voices: {list(data['persona_voices'].keys())}")
        else:
            print(f"[ERROR] Voices check failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error getting voices: {e}")
    
    # Test 3: Set persona voice
    print("\n3. Setting Remo persona voice...")
    try:
        response = requests.post(f"{base_url}/tts/set-persona", json={"persona": "remo"})
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] {data['message']}")
        else:
            print(f"[ERROR] Persona setting failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error setting persona: {e}")
    
    # Test 4: Speak text (blocking)
    print("\n4. Testing blocking speech...")
    try:
        response = requests.post(f"{base_url}/tts/speak", json={
            "text": "Hello! I'm Remo, your friendly AI assistant. How can I help you today?",
            "persona": "remo",
            "blocking": True
        })
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] {data['message']}")
        else:
            print(f"[ERROR] Speech failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error speaking: {e}")
    
    # Test 5: Test different personas
    personas = ["professional", "creative", "remo"]
    for persona in personas:
        print(f"\n5.{personas.index(persona) + 1}. Testing {persona} persona...")
        try:
            response = requests.post(f"{base_url}/tts/speak", json={
                "text": f"This is the {persona} persona speaking.",
                "persona": persona,
                "blocking": True
            })
            if response.status_code == 200:
                data = response.json()
                print(f"[SUCCESS] {persona} persona: {data['message']}")
            else:
                print(f"[ERROR] {persona} speech failed: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Error with {persona}: {e}")
    
    # Test 6: Async speech
    print("\n6. Testing async speech...")
    try:
        response = requests.post(f"{base_url}/tts/speak-async", json={
            "text": "This is an async speech test.",
            "persona": "creative"
        })
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] {data['message']}")
            print("Waiting for async speech to complete...")
            time.sleep(3)  # Wait for speech to complete
        else:
            print(f"[ERROR] Async speech failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error with async speech: {e}")
    
    # Test 7: Generate speech file
    print("\n7. Testing speech-to-file...")
    try:
        response = requests.post(f"{base_url}/tts/speak-to-file", json={
            "text": "This is a test of speech file generation.",
            "persona": "professional",
            "format": "wav"
        })
        if response.status_code == 200:
            print("[SUCCESS] Speech file generated successfully")
            # Save the file
            with open("test_speech.wav", "wb") as f:
                f.write(response.content)
            print("[SUCCESS] File saved as 'test_speech.wav'")
        else:
            print(f"[ERROR] Speech file generation failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error generating speech file: {e}")
    
    # Test 8: Stop speech
    print("\n8. Testing stop speech...")
    try:
        response = requests.post(f"{base_url}/tts/stop")
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] {data['message']}")
        else:
            print(f"[ERROR] Stop speech failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error stopping speech: {e}")
    
    print("\nTTS testing completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_tts_endpoints()
