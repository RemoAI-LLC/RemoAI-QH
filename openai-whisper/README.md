# OpenAI Whisper Integration

This folder contains all the Whisper-related files for the Remo AI chatbot.

## 📁 Files

- **`whisper_service.py`** - Core Whisper functionality for speech-to-text
- **`api_wrapper.py`** - Standalone Whisper API server
- **`audio_utils.py`** - Audio processing utilities
- **`start_whisper_api.py`** - Easy startup script for the unified API
- **`test_whisper.py`** - Test script to verify Whisper integration
- **`WHISPER_INTEGRATION.md`** - Comprehensive documentation

## 🚀 Quick Start

### 1. Start the API Server

```bash
# From the project root
cd openai-whisper
python3 start_whisper_api.py
```

### 2. Test the Integration

```bash
# From the openai-whisper directory
python3 test_whisper.py
```

### 3. Start the Frontend

```bash
# From the project root
cd app-ui
npm start
```

## 📖 Documentation

For detailed information about the Whisper integration, see [WHISPER_INTEGRATION.md](WHISPER_INTEGRATION.md).

## 🔧 Usage

The startup script will:

1. Check for the virtual environment
2. Verify all dependencies are installed
3. Start the unified API server on port 5000
4. Provide endpoints for both text and voice input

The test script will:

1. Test Whisper service initialization
2. Test API server connection
3. Verify the integration is working correctly
