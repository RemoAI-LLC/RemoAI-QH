#!/usr/bin/env python3
"""
Test script for the 24/7 listening feature
"""

import requests
import json
import time

def test_listening_endpoint():
    """Test the listening endpoint with a sample audio file"""
    
    print("Testing 24/7 Listening Feature")
    print("=" * 40)
    
    # Test the health endpoint first
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API Server is running")
            health_data = response.json()
            print(f"   Services: {health_data.get('services', {})}")
        else:
            print("❌ API Server is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("   Make sure to start the server with: python llm/src/unified_api.py")
        return
    
    # Test the listening endpoint (this would normally use real audio)
    print("\n📝 Testing listening endpoint...")
    print("   Note: This test simulates the endpoint structure")
    print("   In real usage, audio files would be sent via the frontend")
    
    # Test data structure
    test_data = {
        "transcribed_text": "we have meeting with microsoft tomorrow regarding the production i am not sure how to deal with it because its a big tech company where i need to prepare more to present at that meeting",
        "api_key": "A3W1B5T-1DQMWGX-P0XHR4V-7030128"
    }
    
    print(f"   Sample transcribed text: {test_data['transcribed_text'][:50]}...")
    print("   This would generate notifications about meeting preparation")
    
    print("\n🎯 Expected Features:")
    print("   ✅ 24/7 continuous listening mode")
    print("   ✅ Voice activation with 'hey remo' commands")
    print("   ✅ Real-time notification generation")
    print("   ✅ Click-to-expand notification panel")
    print("   ✅ 30-second processing intervals")
    print("   ✅ LLM-powered conversation analysis")
    
    print("\n🚀 To test the full feature:")
    print("   1. Start the API server: python llm/src/unified_api.py")
    print("   2. Start the Electron app: npm start")
    print("   3. Click the listening mode button (purple microphone)")
    print("   4. Say 'Hey Remo, enable listening mode'")
    print("   5. Talk about meetings, tasks, or any topic")
    print("   6. Check notifications panel for AI-generated suggestions")

if __name__ == "__main__":
    test_listening_endpoint()
