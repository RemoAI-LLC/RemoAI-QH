# eSpeak TTS Integration for Remo AI

This directory contains the Text-to-Speech (TTS) functionality for Remo AI using eSpeak, providing voice synthesis for AI responses with persona-specific voice characteristics.

## 🎯 Features

- **Persona-Specific Voices**: Different voice characteristics for each AI persona
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **REST API Integration**: Full API endpoints for TTS functionality
- **Async Speech**: Non-blocking speech synthesis
- **File Generation**: Convert text to audio files
- **Voice Customization**: Adjustable speed, pitch, and volume

## 🚀 Quick Start

### 1. Install eSpeak

```bash
# Run the automatic installer
python espeak/install_espeak.py

# Or install manually:
# Windows: choco install espeak
# Linux: sudo apt install espeak-ng
# macOS: brew install espeak-ng
```

### 2. Test TTS Functionality

```bash
# Test all TTS endpoints
python espeak/test_tts.py
```

### 3. Use in Your Application

```python
from espeak.persona_tts import PersonaTTSManager

# Initialize TTS manager
tts = PersonaTTSManager()

# Set persona and speak
tts.set_persona("remo")
tts.speak_persona_response("Hello! How can I help you today?")
```

## 🎭 Persona Voices

### Remo (Default)
- **Voice**: English (en)
- **Speed**: 180 WPM (friendly and conversational)
- **Pitch**: 55 (slightly higher for warmth)
- **Volume**: 100

### Professional
- **Voice**: English US (en-us)
- **Speed**: 160 WPM (slower, more deliberate)
- **Pitch**: 45 (lower, more authoritative)
- **Volume**: 95

### Creative
- **Voice**: English UK (en-gb)
- **Speed**: 200 WPM (faster, more energetic)
- **Pitch**: 60 (higher for enthusiasm)
- **Volume**: 105

## 📡 API Endpoints

### Speak Text
```http
POST /tts/speak
Content-Type: application/json

{
    "text": "Hello, this is Remo speaking!",
    "persona": "remo",
    "blocking": false
}
```

### Speak Asynchronously
```http
POST /tts/speak-async
Content-Type: application/json

{
    "text": "This will be spoken in the background",
    "persona": "creative"
}
```

### Generate Speech File
```http
POST /tts/speak-to-file
Content-Type: application/json

{
    "text": "Save this speech to a file",
    "persona": "professional",
    "format": "wav"
}
```

### Set Persona Voice
```http
POST /tts/set-persona
Content-Type: application/json

{
    "persona": "remo"
}
```

### Stop Speech
```http
POST /tts/stop
```

### Get Status
```http
GET /tts/status
```

### Get Available Voices
```http
GET /tts/voices
```

## 🔧 Configuration

### Custom Persona Voices

```python
from espeak.persona_tts import PersonaTTSManager

tts = PersonaTTSManager()

# Add custom persona voice
custom_voice = {
    "voice": "en-scottish",
    "speed": 170,
    "pitch": 50,
    "volume": 100,
    "description": "Scottish accent voice"
}

tts.add_custom_persona_voice("scottish", custom_voice)
```

### Voice Parameters

- **Speed**: 80-500 words per minute
- **Pitch**: 0-99 (0=lowest, 99=highest)
- **Volume**: 0-200 (0=silent, 200=loudest)

## 🧪 Testing

### Run All Tests
```bash
python espeak/test_tts.py
```

### Test Specific Functionality
```python
# Test basic TTS
from espeak.tts_service import TTSService
tts = TTSService()
tts.speak("Hello, this is a test!")

# Test persona TTS
from espeak.persona_tts import PersonaTTSManager
tts_manager = PersonaTTSManager()
tts_manager.speak_persona_response("Hello from Remo!", "remo")
```

## 🐛 Troubleshooting

### eSpeak Not Found
```bash
# Check if eSpeak is installed
espeak --version

# Install if missing
python espeak/install_espeak.py
```

### No Sound Output
1. Check system volume
2. Verify audio drivers
3. Test with: `espeak "Hello world"`

### Permission Errors
- Windows: Run as Administrator
- Linux: Add user to audio group
- macOS: Grant microphone permissions

### Voice Quality Issues
- Adjust speed, pitch, and volume parameters
- Try different voice codes
- Check eSpeak voice list: `espeak --voices`

## 📁 File Structure

```
espeak/
├── tts_service.py          # Core TTS service
├── persona_tts.py          # Persona-specific TTS manager
├── tts_api.py              # REST API endpoints
├── test_tts.py             # Test script
├── install_espeak.py       # eSpeak installer
└── README.md               # This file
```

## 🔗 Integration with Remo AI

The TTS system integrates seamlessly with Remo AI:

1. **Automatic Persona Switching**: Voice changes with persona
2. **Response Synthesis**: AI responses are automatically spoken
3. **API Integration**: Full REST API for frontend integration
4. **Error Handling**: Graceful fallback when TTS is unavailable

## 📝 Notes

- **eSpeak vs eSpeak-ng**: This system works with both eSpeak and eSpeak-ng
- **Platform Support**: Full support for Windows, macOS, and Linux
- **Performance**: Lightweight and fast speech synthesis
- **Customization**: Highly customizable voice parameters
- **File Formats**: Supports WAV and other audio formats

## 🤝 Contributing

To add new features or fix issues:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see main project LICENSE file for details.
