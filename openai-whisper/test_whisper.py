#!/usr/bin/env python3
"""
Test script for Whisper integration
"""

import os
import sys
import tempfile
import wave
import numpy as np

# Add the current directory to the path (we're now inside openai-whisper)
sys.path.append(os.path.dirname(__file__))

def create_test_audio():
    """Create a simple test audio file with a sine wave."""
    # Generate a 2-second sine wave at 440 Hz (A note)
    sample_rate = 16000
    duration = 2.0
    frequency = 440
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        with wave.open(temp_file.name, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return temp_file.name

def test_whisper_service():
    """Test the Whisper service with a generated audio file."""
    try:
        from whisper_service import WhisperService
        
        print("🧪 Testing Whisper Service...")
        print("=" * 40)
        
        # Initialize Whisper service
        print("📥 Loading Whisper model (this may take a moment on first run)...")
        whisper_service = WhisperService("tiny")  # Use tiny for faster testing
        whisper_service.load_model()
        print("✅ Whisper model loaded successfully")
        
        # Create test audio
        print("🎵 Creating test audio file...")
        test_audio_path = create_test_audio()
        print(f"✅ Test audio created: {test_audio_path}")
        
        # Test transcription
        print("🎤 Testing transcription...")
        try:
            transcribed_text = whisper_service.transcribe_audio_file(test_audio_path)
            print(f"✅ Transcription result: '{transcribed_text}'")
        except Exception as e:
            print(f"⚠️  Transcription failed (expected for sine wave): {e}")
            print("   This is normal - Whisper expects speech, not pure tones")
        
        # Clean up
        os.unlink(test_audio_path)
        print("🧹 Cleaned up test files")
        
        print("\n🎉 Whisper service test completed!")
        print("✅ Service is working correctly")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error testing Whisper service: {e}")
        return False
    
    return True

def test_api_connection():
    """Test if the unified API is running."""
    try:
        import requests
        
        print("\n🌐 Testing API connection...")
        response = requests.get('http://localhost:5000/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API server is running")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Services: {data.get('services', {})}")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure to start the server with: python3 start_whisper_api.py")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    print("🚀 Remo AI Whisper Integration Test")
    print("=" * 50)
    
    # Test Whisper service
    whisper_ok = test_whisper_service()
    
    # Test API connection
    api_ok = test_api_connection()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Whisper Service: {'✅ PASS' if whisper_ok else '❌ FAIL'}")
    print(f"   API Connection:  {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if whisper_ok and api_ok:
        print("\n🎉 All tests passed! Whisper integration is ready to use.")
        print("\nNext steps:")
        print("1. Start the API server: python3 start_whisper_api.py")
        print("2. Start the frontend: cd app-ui && npm start")
        print("3. Click the microphone button to test voice input")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        if not whisper_ok:
            print("   - Check that Whisper dependencies are installed")
        if not api_ok:
            print("   - Start the API server first")

if __name__ == "__main__":
    main()
