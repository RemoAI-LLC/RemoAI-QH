# RemoAI-QH

A comprehensive AI Personal Assistant with voice input, 24/7 listening capable using AnythingLLM and Whisper, featuring human like conversation experience and NPU acceleration capabilities.

Table of Contents

1. [Purpose]
2. [Implementation]
3. [Setup]
4. [Usage]
5. [Troubleshooting]
6. [Contributing]
7. [Code of Conduct]

Purpose

Remois an extensible AI personal Assistant platform designed for privacy-first, local AI interactions. The application integrates a friendly human like conversations through voice recognition,24/7 listening, chat, text-to-speech capabilities, and NPU acceleration for optimal performance. Built with AnythingLLM for LLM functionality and OpenAI Whisper for speech recognition, it provides a complete conversational AI experience.

Key features include:
- **AI Persona**: Friendly and engaging Remo personality which doesn't behave like any other chatbots, llms over there. As a personal assistant it understands rather working like a query based model.
- **Voice Integration**: Real-time speech-to-text and text-to-speech
- **NPU Acceleration**: Optimized for Snapdragon X Elite and other NPU-enabled hardware
- **Privacy-First**: Local processing 
- **Cross-Platform**: Electron-based desktop application

Implementation

This application was designed to be platform-agnostic with optimizations for NPU-enabled hardware. Performance may vary on different hardware configurations.

Hardware

- **Machine**: Dell lattitude 7455
- **Chip**: Snapdragon X Elite, Intel, AMD
- **OS**: Windows 11
- **Memory**: 32 GB

Software

- **Node.js Version**: 16.0.0+
- **Python Version**: 3.8+
- **AnythingLLM LLM Provider**: AnythingLLM NPU (or Qualcomm QNN for older versions)
- **AnythingLLM Chat Model**: Llama 3.2 8B Chat 8K
- **Frontend**: Electron with modern web technologies
- **Backend**: Python Flask API with unified endpoints

Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Electron UI   │◄──►│   Flask API      │◄──►│   AnythingLLM   │
│                 │    │                  │    │                 │
│ • Voice UI      │    │ • Chat Client    │    │ • LLM Provider  │
│ • Audio I/O     │    │ • Whisper API    │    │ • Workspace     │
│                 │    │ • TTS Service    │    │ • Memory        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

Setup
Prerequisites

System Requirements
1. **Node.js 16+** - [Download here](https://nodejs.org/)
2. **Python 3.8+** - [Download here](https://python.org/)
3. **Git** - [Download here](https://git-scm.com/)
4. **Audio System** - Working microphone and speakers/headphones

Core Dependencies
5. **AnythingLLM** - [Download and setup AnythingLLM](https://anythingllm.com/)
6. **OpenAI Whisper** - For speech-to-text functionality
7. **eSpeak/eSpeak-ng** - For text-to-speech functionality

Platform-Specific Dependencies

**Windows:**
- Visual C++ Build Tools (for PyAudio compilation)
- Chocolatey or winget (for eSpeak installation)


Step-by-Step Setup

Phase 1: System Dependencies Installation

1. **Install Platform-Specific Dependencies**

   **Windows:**
   ```powershell
   # Install Visual C++ Build Tools (required for PyAudio)
   # Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   
   # Install Chocolatey (if not already installed)
   Set-ExecutionPolicy Bypass -Scope Process -Force
   [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   
   # Install eSpeak via Chocolatey
   choco install espeak -y
   ```

Phase 2: AnythingLLM Setup

2. **Install and setup AnythingLLM**
   - Download and install AnythingLLM from [https://anythingllm.com/](https://anythingllm.com/)
   - Choose AnythingLLM NPU when prompted to choose an LLM provider to target the NPU
   - Choose a model of your choice (recommended: Llama 3.2 8B Chat 8K)
   - Create a workspace by clicking "+ New Workspace"

3. **Generate an API key**
   - Click the settings button on the bottom of the left panel
   - Open the "Tools" dropdown
   - Click "Developer API"
   - Click "Generate New API Key"
   - Copy and save your API key

Phase 3: RemoAI-QH Installation

4. **Clone and setup the repository**
   ```bash
   # Clone the repository
   git clone https://github.com/RemoAI-LLC/RemoAI-QH.git
   cd RemoAI-QH
   ```

5. **Install Node.js dependencies**
   ```bash
   # Install frontend dependencies
   npm install
   ```

6. **Install Python dependencies**
   ```bash
   # This will create virtual environment and install all Python packages
   npm run setup:python
   
   # Alternative: Manual Python setup
   cd llm
   python -m venv npu-chatbot-env
   
   # Activate virtual environment
   # Windows:
   npu-chatbot-env\Scripts\activate
   # macOS/Linux:
   source npu-chatbot-env/bin/activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

7. **Install and verify eSpeak**
   ```bash
   # Run the automatic eSpeak installer
   python tts/install_espeak.py
   
   # Test eSpeak installation
   espeak --version
   # Should output: eSpeak text-to-speech: version 1.51 or similar
   ```

8. **Install and verify Whisper**
   ```bash
   # Whisper is installed via requirements.txt, but you can verify:
   cd openai-whisper
   python test_whisper.py
   ```

Phase 4: Configuration

9. **Configure the application**
   
   Edit `llm/config.yaml` with your settings:
   ```yaml
   api_key: "your-anythingllm-api-key-here"
   listen_api_key: "your-listen-api-key-here"
   model_server_base_url: "http://localhost:3001/api/v1"
   workspace_slug: "your-workspace-slug"
   stream: true
   stream_timeout: 60
   ```

10. **Get your workspace slug**
    ```bash
    # Run from the llm directory
    cd llm
    python src/workspaces.py
    # Find your workspace and copy its slug from the output
    # Add the slug to the workspace_slug variable in config.yaml
    ```

Phase 5: Testing and Verification

11. **Test the complete setup**
    ```bash
    # Test the model server authentication
    python llm/src/auth.py
    
    # Test persona system
    npm run persona:test
    
    # Test TTS functionality
    npm run tts:test
    
    # Test Whisper integration
    cd openai-whisper
    python test_whisper.py
    ```

12. **Start the application**
    ```bash
    # Start both backend and frontend
    npm start
    
    # Or start components individually:
    # Backend only:
    npm run start:backend-only
    
    # Frontend only:
    npm run start:frontend-only
    ```

Usage

You have multiple options to interact with the AI chatbot:

Desktop Application (Recommended)
```bash
# Start the full application (backend + frontend)
npm start
```

License

MIT License - see [LICENSE](LICENSE) file for details.

Acknowledgments

- [OpenAI Whisper](https://openai.com/research/whisper) for speech recognition
- [AnythingLLM](https://anythingllm.com/) for LLM integration and NPU acceleration
- [Electron](https://electronjs.org/) for cross-platform desktop application framework
- [Flask](https://flask.palletsprojects.com/) for Python API server
- [Gradio](https://gradio.app/) for web interface components
