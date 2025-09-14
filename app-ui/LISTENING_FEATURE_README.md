# 24/7 Listening Mode Feature

## Overview

The 24/7 Listening Mode is an innovative feature that transforms Remo into a true personal assistant that continuously listens to your conversations and provides proactive notifications and suggestions, just like a real human assistant would.

## Key Features

### 🎯 Continuous Listening
- **24/7 Audio Monitoring**: Remo continuously listens to your conversations
- **30-Second Processing**: Audio is processed every 30 seconds for optimal performance
- **Smart Filtering**: Only meaningful conversations (10+ characters) are processed

### 🗣️ Voice Activation
- **"Hey Remo" Commands**: Activate features using natural speech
- **Supported Commands**:
  - "Hey Remo, enable listening mode"
  - "Hey Remo, disable listening mode" 
  - "Hey Remo, show notifications"
  - "Hey Remo, [any question or request]"

### 🔔 Intelligent Notifications
- **AI-Powered Analysis**: LLM processes conversations to generate helpful notifications
- **Context-Aware Suggestions**: Meeting prep, task reminders, resource recommendations
- **Priority-Based**: High, medium, and low priority notifications
- **Click-to-Expand**: Full details available on click

### 🎨 Modern UI
- **Listening Mode Toggle**: Purple gradient button with pulsing animation
- **Notification Panel**: Slide-out panel with notification management
- **Status Indicators**: Real-time listening status and notification badges
- **Responsive Design**: Works on desktop and mobile

## How It Works

### 1. Activation
```
User clicks listening mode button OR says "Hey Remo, enable listening mode"
↓
Remo starts continuous audio recording
↓
Audio is processed every 30 seconds
```

### 2. Processing Pipeline
```
Audio Recording (30s chunks)
↓
Whisper Transcription
↓
LLM Analysis & Notification Generation
↓
UI Notification Display
```

### 3. Example Workflow
```
User: "we have meeting with microsoft tomorrow regarding the production i am not sure how to deal with it because its a big tech company where i need to prepare more to present at that meeting"

Remo generates notification:
Title: "Microsoft Meeting Preparation"
Preview: "Hey wanna prepare on how to present for the big tech companies, then these are some guidelines which would be really helpful. Click to view more"
Full Content: [Detailed preparation guidelines and resources]
```

## Technical Implementation

### Frontend (Electron + HTML/CSS/JS)
- **Continuous MediaRecorder**: Records audio in 30-second chunks
- **Real-time UI Updates**: Dynamic notification badges and status indicators
- **Voice Command Processing**: Pattern matching for "hey remo" activation
- **Notification Management**: Expandable notification system

### Backend (Python + Flask)
- **Whisper Integration**: OpenAI Whisper for speech-to-text conversion
- **LLM Processing**: API integration for conversation analysis
- **Notification Generation**: Structured JSON response format
- **Audio Processing**: Efficient audio file handling and cleanup

### API Endpoints
- `POST /listening/process`: Main endpoint for audio processing
- `GET /health`: Service status check
- `POST /transcribe`: Audio transcription
- `POST /chat`: Regular chat functionality

## Configuration

### API Key Setup
The feature uses the provided API key: `A3W1B5T-1DQMWGX-P0XHR4V-7030128`

### Environment Requirements
- Python 3.8+
- Node.js 16+
- Electron
- Microphone access
- Internet connection for LLM processing

## Usage Instructions

### Starting the Feature
1. **Start the API Server**:
   ```bash
   cd llm/src
   python unified_api.py
   ```

2. **Start the Electron App**:
   ```bash
   cd app-ui
   npm start
   ```

3. **Activate Listening Mode**:
   - Click the purple microphone button, OR
   - Say "Hey Remo, enable listening mode"

### Using Voice Commands
- **"Hey Remo, enable listening mode"** - Start continuous listening
- **"Hey Remo, disable listening mode"** - Stop continuous listening  
- **"Hey Remo, show notifications"** - Open notification panel
- **"Hey Remo, [any question]"** - Process as regular chat

### Managing Notifications
- **View Notifications**: Click the bell icon to open notification panel
- **Expand Details**: Click any notification to see full content
- **Mark as Read**: Notifications automatically mark as read when expanded

## Privacy & Security

### Data Handling
- **Local Processing**: Audio is processed locally using Whisper
- **Temporary Storage**: Audio files are deleted immediately after processing
- **No Persistent Storage**: Conversations are not stored permanently
- **Secure API**: All API communications use HTTPS

### Microphone Access
- **Explicit Permission**: User must grant microphone access
- **Visual Indicators**: Clear UI indicators when listening is active
- **Easy Deactivation**: One-click stop button always available

## Performance Optimization

### Resource Management
- **30-Second Chunks**: Balanced processing frequency
- **Memory Cleanup**: Automatic cleanup of audio data
- **Efficient Transcription**: Only processes meaningful audio
- **Smart Filtering**: Skips empty or very short audio

### Battery Optimization
- **Adaptive Processing**: Reduces processing when no speech detected
- **Background Efficiency**: Minimal CPU usage when idle
- **Smart Intervals**: Adjustable processing frequency

## Troubleshooting

### Common Issues
1. **Microphone Not Working**: Check browser permissions
2. **No Notifications**: Verify API server is running
3. **Poor Transcription**: Ensure clear speech and minimal background noise
4. **High CPU Usage**: Reduce processing frequency if needed

### Debug Mode
Enable debug logging by opening browser developer tools and checking console output.

## Future Enhancements

### Planned Features
- **Custom Wake Words**: User-defined activation phrases
- **Notification Categories**: Organized notification types
- **Voice Responses**: TTS responses to voice commands
- **Smart Scheduling**: Time-based notification delivery
- **Integration APIs**: Connect with calendar, email, task apps

### Advanced AI Features
- **Context Memory**: Remember previous conversations
- **Learning Patterns**: Adapt to user preferences
- **Proactive Suggestions**: Anticipate user needs
- **Multi-language Support**: Support for multiple languages

## Support

For issues or questions about the 24/7 Listening Mode feature:
1. Check the troubleshooting section above
2. Review console logs for error messages
3. Ensure all dependencies are properly installed
4. Verify API key and network connectivity

---

**Note**: This feature represents a significant advancement in personal AI assistance, providing a truly hands-free, proactive assistant experience that learns from your conversations and provides intelligent, contextual support.
