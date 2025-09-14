"""
API Wrapper for Whisper Service
Provides HTTP endpoints for speech-to-text functionality
"""

import os
import sys
import tempfile
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import json

# Add the parent directory to the path to import whisper_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from openai_whisper.whisper_service import WhisperService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Whisper service
whisper_service = None

def init_whisper_service(model_size="base"):
    """Initialize the Whisper service."""
    global whisper_service
    try:
        whisper_service = WhisperService(model_size)
        whisper_service.load_model()
        logger.info("Whisper service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Whisper service: {e}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "whisper-api"})

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Transcribe audio file to text.
    
    Expected form data:
    - audio: Audio file (wav, mp3, m4a, etc.)
    """
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No audio file selected"}), 400
        
        # Save the uploaded file temporarily
        filename = secure_filename(audio_file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
            audio_file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe the audio
            if whisper_service is None:
                init_whisper_service()
            
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
def transcribe_audio_data():
    """
    Transcribe raw audio data to text.
    
    Expected JSON data:
    - audio_data: Base64 encoded audio data
    """
    try:
        data = request.get_json()
        if not data or 'audio_data' not in data:
            return jsonify({"error": "No audio data provided"}), 400
        
        # Decode base64 audio data
        import base64
        audio_data = base64.b64decode(data['audio_data'])
        
        # Transcribe the audio
        if whisper_service is None:
            init_whisper_service()
        
        transcribed_text = whisper_service.transcribe_audio_data(audio_data)
        
        return jsonify({
            "success": True,
            "text": transcribed_text
        })
    
    except Exception as e:
        logger.error(f"Error in transcribe-data endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/start-recording', methods=['POST'])
def start_recording():
    """Start recording audio from microphone."""
    try:
        if whisper_service is None:
            init_whisper_service()
        
        data = request.get_json() or {}
        sample_rate = data.get('sample_rate', 16000)
        chunk_size = data.get('chunk_size', 1024)
        
        whisper_service.start_recording(sample_rate, chunk_size)
        
        return jsonify({
            "success": True,
            "message": "Recording started"
        })
    
    except Exception as e:
        logger.error(f"Error starting recording: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stop-recording', methods=['POST'])
def stop_recording():
    """Stop recording and return transcribed text."""
    try:
        if whisper_service is None:
            return jsonify({"error": "Whisper service not initialized"}), 400
        
        audio_data = whisper_service.stop_recording()
        
        if not audio_data:
            return jsonify({"error": "No audio data recorded"}), 400
        
        transcribed_text = whisper_service.transcribe_audio_data(audio_data)
        
        return jsonify({
            "success": True,
            "text": transcribed_text
        })
    
    except Exception as e:
        logger.error(f"Error stopping recording: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Initialize Whisper service on startup
    try:
        init_whisper_service()
        logger.info("Starting Whisper API server on port 5001")
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Whisper API server: {e}")
        sys.exit(1)
