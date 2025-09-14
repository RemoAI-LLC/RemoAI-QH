# RemoAI-QH

AI chatbot with voice input using AnythingLLM and OpenAI Whisper, featuring multiple AI personas.

## 🚀 Quick Start

### Prerequisites
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **Python 3.8+** - [Download here](https://python.org/)
- **AnythingLLM** (optional) - For LLM functionality

### One-Command Setup & Launch

```bash
# Clone the repository
git clone https://github.com/RemoAI-LLC/RemoAI-QH.git
cd RemoAI-QH

# Install everything and start the app
npm install && npm start
```

That's it! The setup script will automatically:
- ✅ Install Node.js dependencies
- ✅ Create Python virtual environment
- ✅ Install Python dependencies
- ✅ Set up configuration files
- ✅ Start both backend and frontend

## 🎭 AI Personas

Remo AI comes with 3 built-in personas:

### 🤖 Remo (Default)
- **Style**: Friendly, warm, and encouraging
- **Use Case**: General conversations and support
- **Characteristics**: Uses emojis, asks follow-up questions, patient

### 💼 Professional
- **Style**: Business-focused and efficient
- **Use Case**: Professional communications and analysis
- **Characteristics**: Direct, solution-focused, formal language

### 🎨 Creative
- **Style**: Imaginative and artistic
- **Use Case**: Creative writing and brainstorming
- **Characteristics**: Vivid language, metaphors, inspiring

## 📋 Available Commands

```bash
# Install all dependencies
npm install

# Start both backend and frontend
npm start

# Start only backend (API server)
npm run start:backend-only

# Start only frontend (Electron app)
npm run start:frontend-only

# Test the persona system
npm run persona:test

# Open persona demo in browser
npm run persona:demo

# Build the Electron app
npm run build

# Clean all dependencies
npm run clean

# Reset everything and reinstall
npm run reset
```

## 🔧 Configuration

### Backend Configuration
Edit `llm/config.yaml` to configure your AnythingLLM connection:

```yaml
api_key: "your-api-key-here"
model_server_base_url: "http://localhost:3001/api/v1"
workspace_slug: "remo"
stream: true
stream_timeout: 60
```

### Persona Configuration
Personas are configured in `llm/persona.yaml`. You can:
- Modify existing personas
- Add custom personas
- Change default persona

## 🌐 API Endpoints

The backend provides these REST API endpoints:

- `GET /health` - Health check
- `POST /chat` - Send text message
- `POST /transcribe` - Transcribe audio file
- `POST /speak-and-chat` - Complete voice workflow
- `GET /personas` - List available personas
- `POST /personas/{name}` - Switch persona
- `GET /personas/current` - Get current persona

## 🎯 Usage

### Text Chat
1. Type your message in the input field
2. Press Enter or click Send
3. The AI will respond using the current persona

### Voice Chat
1. Click the microphone button
2. Speak your message
3. Click the microphone again to send
4. The AI will transcribe and respond

### Switch Personas
1. Use the persona selector in the UI
2. Or use the API: `POST /personas/{persona_name}`
3. Available personas: `remo`, `professional`, `creative`

## 🧪 Testing

```bash
# Test persona system
npm run persona:test

# Test frontend
npm run test:frontend

# Test backend
npm run test:backend

# Test everything
npm test
```

## 📁 Project Structure

```
RemoAI-QH/
├── app-ui/                 # Electron frontend
│   ├── main.js            # Main Electron process
│   ├── renderer.js        # Renderer process
│   ├── persona-manager.js # Persona management
│   └── persona-demo.html  # Interactive demo
├── llm/                   # Python backend
│   ├── src/               # Source code
│   │   ├── unified_api.py # Main API server
│   │   ├── chat_client.py # LLM client
│   │   └── persona.py     # Persona system
│   ├── config.yaml        # Backend configuration
│   └── persona.yaml       # Persona configurations
├── scripts/               # Setup scripts
│   ├── setup-python.js   # Python environment setup
│   └── start-backend.js  # Backend startup
└── package.json          # Unified package management
```

## 🛠️ Development

### Adding New Personas

1. Edit `llm/persona.yaml` or use the API
2. Add persona configuration:

```yaml
personas:
  my_persona:
    name: "My Custom Assistant"
    description: "A custom AI assistant"
    system_prompt: "You are a custom assistant..."
    greeting: "Hello! I'm your custom assistant."
    voice_style: "custom style"
    response_style: "custom responses"
```

### Frontend Integration

```javascript
// Use PersonaManager in your app
const personaManager = new PersonaManager();

// Load personas
await personaManager.loadPersonas();

// Switch persona
await personaManager.setPersona('professional');

// Send message
const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Hello!' })
});
```

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Run `npm install` to set up Python environment
- Check if Python 3.8+ is installed
- Verify virtual environment exists in `llm/npu-chatbot-env/`

**Frontend won't start:**
- Run `npm install` in the root directory
- Check if Node.js 16+ is installed
- Try `npm run clean && npm install`

**Persona switching not working:**
- Check if backend is running on port 8000
- Verify persona configuration in `llm/persona.yaml`
- Test with `npm run persona:test`

**Audio/Whisper issues:**
- Ensure microphone permissions are granted
- Check if PyAudio is properly installed
- Try different audio formats

### Getting Help

1. Check the logs in the terminal
2. Run `npm run persona:test` to test the system
3. Open `app-ui/persona-demo.html` for interactive testing
4. Check the API health: `curl http://localhost:8000/health`

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- AnythingLLM for LLM integration
- Electron for cross-platform desktop app
- Flask for Python API server

---

**Made with ❤️ by the RemoAI Team**