# NPU-Accelerated Chatbot with AnythingLLM

A simple, NPU-accelerated chatbot running locally using AnythingLLM with Llama 3.2 2B 8K model. This chatbot is designed to leverage NPU acceleration for faster, more efficient local AI conversations.

## Features

- 🤖 **NPU Acceleration**: Optimized for Snapdragon X Elite NPU
- 🚀 **Fast Responses**: Streamed responses for real-time interaction
- 💬 **Multiple Interfaces**: Terminal and web-based Gradio interface
- 🔒 **Private & Local**: All processing happens on your device
- 📝 **Conversation Memory**: Maintains context throughout the conversation
- ⚙️ **Easy Configuration**: Simple YAML-based configuration

## Hardware Requirements

- **Recommended**: Snapdragon X Elite with NPU support
- **OS**: Windows 11 (ARM64)
- **Memory**: 8GB+ RAM recommended
- **Storage**: 5GB+ free space for model and dependencies

## Software Requirements

- Python 3.8+
- AnythingLLM (ARM64 version)
- Llama 3.2 2B 8K model

## Setup Instructions

### 1. Install AnythingLLM

1. Download and install AnythingLLM (ARM64 version)
2. Choose "AnythingLLM NPU" as the LLM provider
3. Select "Llama 3.2 2B 8K" model
4. Create a new workspace
5. Generate an API key in Settings → Tools → Developer API

### 2. Clone and Setup Project

```bash
# Clone the repository
git clone <your-repo-url>
cd test-npu

# Create virtual environment
python -m venv npu-chatbot-env

# Activate virtual environment
# Windows:
npu-chatbot-env\\Scripts\\activate
# macOS/Linux:
source npu-chatbot-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure the Application

1. Update `config.yaml` with your settings:
```yaml
api_key: "your-anythingllm-api-key-here"
model_server_base_url: "http://localhost:3001/api/v1"
workspace_slug: "your-workspace-slug-here"
stream: true
stream_timeout: 60
```

2. Get your workspace slug:
```bash
cd llm
python src/workspaces.py
```

3. Test authentication:
```bash
cd llm
python src/auth.py
```

## Usage

### Terminal Interface

Run the terminal-based chatbot:
```bash
cd llm
python src/terminal_chatbot.py
```

**Available Commands:**
- `quit`, `exit`, `bye` - End the conversation
- `clear` - Clear conversation history
- `help` - Show help information
- `history` - Show conversation history

### Web Interface (Gradio)

Run the web-based chatbot:
```bash
cd llm
python src/gradio_chatbot.py
```

Then open your browser to `http://localhost:7860`

### Electron Desktop App

Run the modern desktop application:
```bash
cd app-ui
npm start
```

**Features:**
- Modern, responsive chat interface
- Real-time streaming responses
- Settings management
- Cross-platform desktop app

## Troubleshooting

### NPU Not Detected
- Ensure you installed the ARM64 version of AnythingLLM
- Check that your system supports NPU acceleration
- Verify the model is properly downloaded in AnythingLLM

### Authentication Issues
- Verify your API key is correct
- Ensure AnythingLLM is running on the correct port
- Check that your workspace slug is valid

### Model Not Loading
- Verify the model is downloaded in AnythingLLM settings
- Try switching to another model and back
- Check available disk space

### Connection Errors
- Ensure AnythingLLM is running
- Check firewall settings
- Verify the API URL in config.yaml

## Project Structure

```
test-npu/
├── llm/                     # LLM backend components
│   ├── src/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication utilities
│   │   ├── workspaces.py        # Workspace management
│   │   ├── chat_client.py       # Core chat functionality
│   │   ├── terminal_chatbot.py  # Terminal interface
│   │   ├── gradio_chatbot.py    # Web interface
│   │   └── api_wrapper.py       # API wrapper for Electron
│   ├── config.yaml              # Configuration file
│   └── requirements.txt         # Python dependencies
├── app-ui/                  # Electron frontend
│   ├── main.js              # Main Electron process
│   ├── index.html           # Chat interface
│   ├── styles.css           # Styling
│   ├── renderer.js          # Frontend logic
│   └── package.json         # Node.js dependencies
└── README.md               # This file
```

## API Reference

The chatbot uses the AnythingLLM API with the following endpoints:
- `GET /user` - User authentication
- `GET /workspaces` - List workspaces
- `POST /workspace/{slug}/chat` - Send chat messages

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Based on the [simple-npu-chatbot](https://github.com/thatrandomfrenchdude/simple-npu-chatbot) template
- Powered by AnythingLLM and Llama 3.2
- Optimized for Snapdragon X Elite NPU
