# RemoAI-QH

AI chatbot with voice input using AnythingLLM and OpenAI Whisper.

## Quick Start

### 1. Install Dependencies

**Frontend:**

```bash
cd app-ui
npm install
```

**Backend:**

```bash
cd llm
python3 -m venv npu-chatbot-env
source npu-chatbot-env/bin/activate  # On Windows: npu-chatbot-env\Scripts\activate
pip3 install -r requirements.txt
```

### 2. Configure

Copy `llm/config.yaml.example` to `llm/config.yaml` and update with your AnythingLLM settings:

```yaml
anythingllm:
  base_url: "http://localhost:3001"
  api_key: "your-api-key-here"
  workspace_id: "your-workspace-id"
```

### 3. Run the Application

**Start the API server (LLM + Whisper):**

```bash
cd openai-whisper
python3 start_whisper_api.py
```

**Start the frontend:**

```bash
cd app-ui
npm start
```

### 4. Use the App

- **Text chat**: Type in the input field and press Enter
- **Voice chat**: Click the microphone button, speak, and click again to send

## Troubleshooting

- **Port conflicts**: The API runs on port 8000. If busy, change port in `llm/src/unified_api.py`
- **Python issues**: Use `pip3` instead of `pip` on macOS
- **Connection errors**: Ensure AnythingLLM is running and configuration is correct
