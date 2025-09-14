#!/usr/bin/env python3
"""
Test script for Remo AI personas
"""

import requests
import json
import time

def test_persona_endpoints():
    """Test the persona API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Remo AI Persona System")
    print("=" * 50)
    
    # Test 1: Get available personas
    print("\n1. Getting available personas...")
    try:
        response = requests.get(f"{base_url}/personas")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available personas: {data['personas']}")
            print(f"✅ Current persona: {data['current_persona']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Test 2: Get current persona details
    print("\n2. Getting current persona details...")
    try:
        response = requests.get(f"{base_url}/personas/current")
        if response.status_code == 200:
            data = response.json()
            persona_info = data['persona_info']
            print(f"✅ Current persona: {data['current_persona']}")
            print(f"✅ Name: {persona_info.get('name', 'N/A')}")
            print(f"✅ Description: {persona_info.get('description', 'N/A')}")
            print(f"✅ Greeting: {persona_info.get('greeting', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Switch to professional persona
    print("\n3. Switching to professional persona...")
    try:
        response = requests.post(f"{base_url}/personas/professional")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Test chat with professional persona
    print("\n4. Testing chat with professional persona...")
    try:
        chat_data = {"message": "Hello, can you help me with a business proposal?"}
        response = requests.post(f"{base_url}/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Professional response: {data['message'][:100]}...")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Switch to creative persona
    print("\n5. Switching to creative persona...")
    try:
        response = requests.post(f"{base_url}/personas/creative")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Test chat with creative persona
    print("\n6. Testing chat with creative persona...")
    try:
        chat_data = {"message": "I need help writing a story about a robot."}
        response = requests.post(f"{base_url}/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Creative response: {data['message'][:100]}...")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Switch back to default persona
    print("\n7. Switching back to default Remo persona...")
    try:
        response = requests.post(f"{base_url}/personas/remo")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Persona testing completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_persona_endpoints()
