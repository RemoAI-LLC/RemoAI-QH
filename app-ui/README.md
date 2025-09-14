# Remo AI - Electron Frontend

This is the Electron.js frontend for Remo AI, a privacy-first personal AI assistant powered by NPU acceleration.

## Features

- 🤖 **Modern Chat Interface**: Clean, responsive design with real-time messaging
- ⚡ **NPU Acceleration**: Powered by Llama 3.2 2B 8K with NPU optimization
- 🔒 **Privacy-First**: All processing happens locally on your device
- 💬 **Streaming Responses**: Real-time character-by-character response display
- ⚙️ **Settings Management**: Easy configuration of API settings
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Python environment with the NPU chatbot backend running

## Installation

1. Navigate to the app-ui directory:
```bash
cd app-ui
```

2. Install dependencies:
```bash
npm install
```

3. Make sure your NPU chatbot backend is running and configured properly.

## Running the Application

### Development Mode
```bash
npm run dev
```

### Production Mode
```bash
npm start
```

## Building the Application

### Build for Current Platform
```bash
npm run build
```

### Create Distribution Package
```bash
npm run dist
```

## Configuration

The app will automatically load configuration from the parent directory's `config.yaml` file. You can also configure settings through the in-app settings modal.

### Required Configuration
- API Key: Your AnythingLLM API key
- Workspace Slug: The slug of your workspace
- API URL: The base URL for the AnythingLLM API (default: http://localhost:3001/api/v1)

## Features Overview

### Chat Interface
- Real-time messaging with the NPU-accelerated Llama 3.2 model
- Streaming responses for better user experience
- Message history and conversation management
- Character count and input validation

### Settings
- API configuration management
- Streaming response toggle
- Workspace and endpoint configuration

### Status Indicators
- Connection status
- Model information (Llama 3.2 2B 8K with NPU)
- Privacy indicator (Local Processing)
- Message count

## Architecture

The application uses Electron.js with the following structure:

- `main.js`: Main Electron process, handles IPC communication with Python backend
- `index.html`: Main UI structure
- `styles.css`: Modern, responsive styling
- `renderer.js`: Frontend JavaScript logic and UI interactions

## Integration with NPU Backend

The frontend communicates with the Python NPU chatbot backend through Electron's IPC system:

- `send-chat-message`: Send regular chat messages
- `send-streaming-chat-message`: Send messages with streaming responses
- `clear-chat-history`: Clear conversation history
- `get-chat-history`: Retrieve conversation history
- `check-config`: Validate configuration

## Troubleshooting

### Common Issues

1. **Connection Error**: Make sure the NPU chatbot backend is running
2. **Configuration Error**: Check that `config.yaml` exists and is properly formatted
3. **API Key Issues**: Verify your AnythingLLM API key and workspace slug

### Development

To run in development mode with DevTools:
```bash
npm run dev
```

This will open the application with developer tools enabled for debugging.

## License

MIT License - see LICENSE for details.
