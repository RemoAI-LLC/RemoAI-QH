# Whisper Integration for Remo AI

This document describes the OpenAI Whisper integration that adds speech-to-text functionality to the Remo AI chatbot.

## 🎤 Features

- **Voice Input**: Click the microphone button to record audio
- **Real-time Transcription**: Uses OpenAI Whisper for accurate speech-to-text conversion
- **Seamless Integration**: Voice input flows directly into the LLM conversation
- **Visual Feedback**: Microphone button changes state during recording
- **Multiple Audio Formats**: Supports WebM, WAV, MP3, and other common formats

## 📁 Project Structure

```
RemoAI-QH/
├── openai-whisper/              # Whisper integration package
│   ├── __init__.py
│   ├── whisper_service.py       # Core Whisper functionality
│   ├── api_wrapper.py          # Standalone Whisper API
│   ├── audio_utils.py          # Audio processing utilities
│   ├── start_whisper_api.py    # Easy startup script
│   ├── test_whisper.py         # Test script
│   └── WHISPER_INTEGRATION.md  # This documentation
├── llm/
│   ├── src/
│   │   ├── unified_api.py      # Combined LLM + Whisper API
│   │   └── ...                 # Existing LLM files
│   └── requirements.txt        # Updated with Whisper dependencies
└── app-ui/                     # Frontend with mic button
    ├── index.html              # Updated with voice input
    ├── renderer.js             # Voice recording logic
    └── styles.css              # Recording state styles
```

## 🚀 Quick Start

### 1. Install Dependencies

The Whisper dependencies are already included in the updated `requirements.txt`. If you haven't installed them yet:

```bash
cd llm
source npu-chatbot-env/bin/activate
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
# From the project root
cd openai-whisper
python3 start_whisper_api.py
```

This will start the unified API server on port 5000 with both LLM and Whisper functionality.

### 3. Start the Frontend

```bash
cd app-ui
npm start
```

### 4. Use Voice Input

1. Click the microphone button in the chat interface
2. Grant microphone permissions when prompted
3. Speak your message
4. Click the microphone button again to stop recording
5. The audio will be transcribed and sent to the LLM automatically

## 🔧 API Endpoints

The unified API server provides the following endpoints:

### Text Chat

- `POST /chat` - Send text message to LLM
  ```json
  {
    "message": "Hello, how are you?",
    "stream": true
  }
  ```

### Voice Input

- `POST /transcribe` - Transcribe audio file

  - Form data with `audio` file
  - Returns transcribed text

- `POST /speak-and-chat` - Complete voice workflow
  - Form data with `audio` file and `stream` option
  - Returns both transcribed text and LLM response

### Utility

- `GET /health` - Health check
- `POST /clear-history` - Clear conversation history
- `GET /history` - Get conversation history

## 🎯 How It Works

### Frontend (renderer.js)

1. **Voice Button Click**: User clicks microphone button
2. **Media Access**: Browser requests microphone permission
3. **Audio Recording**: MediaRecorder captures audio in WebM format
4. **Stop Recording**: User clicks button again to stop
5. **Audio Processing**: Audio chunks are combined into a blob
6. **API Call**: Audio is sent to `/speak-and-chat` endpoint
7. **Display Results**: Both transcribed text and LLM response are shown

### Backend (unified_api.py)

1. **Audio Reception**: Flask receives the audio file
2. **Whisper Processing**: Audio is transcribed using OpenAI Whisper
3. **LLM Integration**: Transcribed text is sent to the existing LLM client
4. **Response**: Both transcription and LLM response are returned

### Whisper Service (whisper_service.py)

- **Model Loading**: Loads Whisper model (default: "base")
- **Audio Processing**: Handles various audio formats
- **Transcription**: Converts speech to text with high accuracy
- **Error Handling**: Robust error handling and logging

## ⚙️ Configuration

### Whisper Model Size

You can change the Whisper model size in `unified_api.py`:

```python
# Available models: tiny, base, small, medium, large
whisper_service = WhisperService("base")  # Change this
```

Model sizes and their characteristics:

- **tiny**: Fastest, least accurate (~39 MB)
- **base**: Good balance (~74 MB) - **Default**
- **small**: Better accuracy (~244 MB)
- **medium**: High accuracy (~769 MB)
- **large**: Best accuracy (~1550 MB)

### Audio Settings

The frontend is configured for optimal Whisper performance:

- Sample rate: 16kHz
- Channels: Mono (1 channel)
- Echo cancellation: Enabled
- Noise suppression: Enabled

## 🐛 Troubleshooting

### Microphone Access Issues

- Ensure your browser has microphone permissions
- Check that no other applications are using the microphone
- Try refreshing the page and granting permissions again

### Audio Quality Issues

- Speak clearly and at a normal volume
- Reduce background noise
- Ensure microphone is working in other applications

### API Connection Issues

- Verify the API server is running on port 5000
- Check that all dependencies are installed
- Look at the console for error messages

### Whisper Model Issues

- First run will download the model (may take time)
- Ensure sufficient disk space for the model
- Check internet connection for model download

## 🔍 Debugging

### Enable Debug Logging

The API server runs in debug mode by default. Check the console output for detailed logs.

### Test Whisper Directly

You can test Whisper independently:

```python
from openai_whisper.whisper_service import WhisperService

service = WhisperService("base")
service.load_model()
text = service.transcribe_audio_file("path/to/audio.wav")
print(text)
```

### Test API Endpoints

Use curl to test the API:

```bash
# Test health
curl http://localhost:5000/health

# Test transcription
curl -X POST -F "audio=@test.wav" http://localhost:5000/transcribe
```

## 📊 Performance Notes

- **First Run**: Model download and initialization takes time
- **Memory Usage**: Base model uses ~1GB RAM
- **Processing Time**: Transcription typically takes 1-3 seconds
- **Audio Length**: Longer audio takes proportionally longer to process

## 🔒 Privacy & Security

- All audio processing happens locally on your device
- No audio data is sent to external services (except your LLM API)
- Audio files are temporarily stored only during processing
- Microphone access is only requested when needed

## 🚀 Future Enhancements

Potential improvements for the Whisper integration:

1. **Real-time Streaming**: Continuous audio transcription
2. **Audio Format Conversion**: Better WebM to WAV conversion
3. **Voice Commands**: Special commands for app control
4. **Multiple Languages**: Language detection and selection
5. **Audio Visualization**: Visual feedback during recording
6. **Offline Mode**: Complete offline operation

## 📝 License

This Whisper integration follows the same MIT license as the main project.
