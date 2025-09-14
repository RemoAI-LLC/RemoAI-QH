"""
Unified API server for LLM and Whisper integration
"""

import os
import sys
import json
import tempfile
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import base64

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'openai-whisper'))

from chat_client import NPUChatClient
from whisper_service import WhisperService
from audio_utils import convert_audio_to_wav, convert_wav_to_base64

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize services
chat_client = None
whisper_service = None

def init_services():
    """Initialize both chat and whisper services."""
    global chat_client, whisper_service
    
    try:
        # Initialize chat client
        chat_client = NPUChatClient('config.yaml')
        logger.info("Chat client initialized successfully")
        
        # Initialize whisper service
        whisper_service = WhisperService("base")
        whisper_service.load_model()
        logger.info("Whisper service initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy", 
        "services": {
            "chat": chat_client is not None,
            "whisper": whisper_service is not None
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """
    Send a text message to the LLM.
    
    Expected JSON data:
    - message: Text message to send
    - stream: Whether to stream the response (optional, default: true)
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        
        message = data['message']
        stream = data.get('stream', True)
        
        if chat_client is None:
            init_services()
        
        if stream:
            # Stream the response
            response_chunks = []
            for chunk in chat_client.send_message(message, True):
                response_chunks.append(chunk)
            
            full_response = ''.join(response_chunks)
            return jsonify({
                "success": True,
                "message": full_response,
                "streamed": True
            })
        else:
            # Get complete response
            response = chat_client.send_message(message, False)
            return jsonify({
                "success": True,
                "message": response,
                "streamed": False
            })
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Transcribe audio to text using Whisper.
    
    Expected form data:
    - audio: Audio file (wav, mp3, m4a, etc.)
    """
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No audio file selected"}), 400
        
        if whisper_service is None:
            init_services()
        
        # Save the uploaded file temporarily
        filename = secure_filename(audio_file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
            audio_file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe the audio
            transcribed_text = whisper_service.transcribe_audio_file(temp_file_path)
            
            return jsonify({
                "success": True,
                "text": transcribed_text,
                "filename": filename
            })
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except Exception as e:
        logger.error(f"Error in transcribe endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/transcribe-data', methods=['POST'])
def transcribe_data():
    """
    Transcribe raw audio data to text.
    
    Expected JSON data:
    - audio_data: Base64 encoded audio data
    """
    try:
        data = request.get_json()
        if not data or 'audio_data' not in data:
            return jsonify({"error": "No audio data provided"}), 400
        
        if whisper_service is None:
            init_services()
        
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio_data'])
        
        # Transcribe the audio
        transcribed_text = whisper_service.transcribe_audio_data(audio_data)
        
        return jsonify({
            "success": True,
            "text": transcribed_text
        })
    
    except Exception as e:
        logger.error(f"Error in transcribe-data endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/speak-and-chat', methods=['POST'])
def speak_and_chat():
    """
    Complete workflow: transcribe audio -> send to LLM -> return response.
    
    Expected form data:
    - audio: Audio file
    - stream: Whether to stream LLM response (optional, default: true)
    """
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No audio file selected"}), 400
        
        stream = request.form.get('stream', 'true').lower() == 'true'
        
        if chat_client is None or whisper_service is None:
            init_services()
        
        # Save the uploaded file temporarily
        filename = secure_filename(audio_file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
            audio_file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Step 1: Transcribe audio
            transcribed_text = whisper_service.transcribe_audio_file(temp_file_path)
            
            if not transcribed_text.strip():
                return jsonify({"error": "No speech detected in audio"}), 400
            
            # Step 2: Send to LLM
            if stream:
                # Stream the response
                response_chunks = []
                for chunk in chat_client.send_message(transcribed_text, True):
                    response_chunks.append(chunk)
                
                full_response = ''.join(response_chunks)
                return jsonify({
                    "success": True,
                    "transcribed_text": transcribed_text,
                    "llm_response": full_response,
                    "streamed": True
                })
            else:
                # Get complete response
                llm_response = chat_client.send_message(transcribed_text, False)
                return jsonify({
                    "success": True,
                    "transcribed_text": transcribed_text,
                    "llm_response": llm_response,
                    "streamed": False
                })
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except Exception as e:
        logger.error(f"Error in speak-and-chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear conversation history."""
    try:
        if chat_client is None:
            init_services()
        
        chat_client.clear_history()
        return jsonify({"success": True, "message": "History cleared"})
    
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history."""
    try:
        if chat_client is None:
            init_services()
        
        history = chat_client.get_history()
        return jsonify({"success": True, "history": history})
    
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        # Initialize services on startup
        init_services()
        logger.info("Starting unified API server on port 8000")
        app.run(host='0.0.0.0', port=8000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start unified API server: {e}")
        sys.exit(1)
