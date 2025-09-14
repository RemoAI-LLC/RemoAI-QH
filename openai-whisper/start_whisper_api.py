#!/usr/bin/env python3
"""
Startup script for the unified Whisper + LLM API server
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 Starting Remo AI with Whisper Integration...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('../llm/config.yaml'):
        print("❌ Error: config.yaml not found. Please run this from the project root directory.")
        sys.exit(1)
    
    # Check if virtual environment exists
    venv_path = '../llm/npu-chatbot-env'
    if not os.path.exists(venv_path):
        print("❌ Error: Virtual environment not found. Please run setup first.")
        print("Run: cd llm && python3 -m venv npu-chatbot-env && source npu-chatbot-env/bin/activate && pip install -r requirements.txt")
        sys.exit(1)
    
    # Get the Python executable from the virtual environment
    if sys.platform == "win32":
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_exe = os.path.join(venv_path, "bin", "python")
    
    if not os.path.exists(python_exe):
        print(f"❌ Error: Python executable not found at {python_exe}")
        sys.exit(1)
    
    print("✅ Virtual environment found")
    print("✅ Dependencies installed")
    print()
    
    # Start the unified API server
    api_script = os.path.join('..', 'llm', 'src', 'unified_api.py')
    if not os.path.exists(api_script):
        print(f"❌ Error: API script not found at {api_script}")
        sys.exit(1)
    
    print("🎤 Starting Whisper + LLM API server on port 8000...")
    print("📡 API endpoints:")
    print("   - POST /chat - Send text message to LLM")
    print("   - POST /transcribe - Transcribe audio file")
    print("   - POST /speak-and-chat - Complete voice workflow")
    print("   - GET /health - Health check")
    print()
    print("🌐 Frontend will connect to: http://localhost:8000")
    print("=" * 50)
    print()
    
    try:
        # Change to the llm directory and start the server
        os.chdir('../llm')
        subprocess.run([python_exe, 'src/unified_api.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down API server...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
