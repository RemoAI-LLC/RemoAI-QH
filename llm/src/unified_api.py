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

# Import TTS functionality
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tts'))
from persona_tts import PersonaTTSManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize services
chat_client = None
whisper_service = None
tts_manager = None

def init_services():
    """Initialize chat, whisper, and TTS services."""
    global chat_client, whisper_service, tts_manager
    
    try:
        # Initialize whisper service first (doesn't require external server)
        whisper_service = WhisperService("base")
        whisper_service.load_model()
        logger.info("Whisper service initialized successfully")
        
        # Initialize TTS service
        try:
            tts_manager = PersonaTTSManager()
            logger.info("TTS service initialized successfully")
        except Exception as tts_error:
            logger.warning(f"TTS service initialization failed: {tts_error}")
            tts_manager = None
        
        # Try to initialize chat client (may fail if AnythingLLM is not running)
        try:
            chat_client = NPUChatClient('config.yaml')
            logger.info("Chat client initialized successfully")
        except Exception as chat_error:
            logger.warning(f"Chat client initialization failed (AnythingLLM may not be running): {chat_error}")
            chat_client = None
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Don't raise the exception, allow the server to start with limited functionality
        whisper_service = None
        tts_manager = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy", 
        "services": {
            "chat": chat_client is not None,
            "whisper": whisper_service is not None,
            "tts": tts_manager is not None
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
        
        if chat_client is None:
            return jsonify({"error": "Chat service not available. Please ensure AnythingLLM is running."}), 503
        
        if stream:
            # Stream the response
            response_chunks = []
            for chunk in chat_client.send_message(message, True):
                response_chunks.append(chunk)
            
            full_response = ''.join(response_chunks)
            
            # Speak the response if TTS is available
            if tts_manager is not None:
                try:
                    current_persona = chat_client.get_current_persona() if chat_client else "remo"
                    tts_manager.speak_persona_response_async(full_response, current_persona)
                except Exception as tts_error:
                    logger.warning(f"TTS error: {tts_error}")
            
            return jsonify({
                "success": True,
                "message": full_response,
                "streamed": True
            })
        else:
            # Get complete response
            response = chat_client.send_message(message, False)
            
            # Speak the response if TTS is available
            if tts_manager is not None:
                try:
                    current_persona = chat_client.get_current_persona() if chat_client else "remo"
                    tts_manager.speak_persona_response_async(response, current_persona)
                except Exception as tts_error:
                    logger.warning(f"TTS error: {tts_error}")
            
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
        
        if chat_client is None:
            return jsonify({"error": "Chat service not available. Please ensure AnythingLLM is running."}), 503
        
        if whisper_service is None:
            return jsonify({"error": "Whisper service not available."}), 503
        
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
                
                # Step 3: Speak the response if TTS is available
                if tts_manager is not None:
                    try:
                        current_persona = chat_client.get_current_persona() if chat_client else "remo"
                        tts_manager.speak_persona_response_async(full_response, current_persona)
                    except Exception as tts_error:
                        logger.warning(f"TTS error in speak-and-chat: {tts_error}")
                
                return jsonify({
                    "success": True,
                    "transcribed_text": transcribed_text,
                    "llm_response": full_response,
                    "streamed": True
                })
            else:
                # Get complete response
                llm_response = chat_client.send_message(transcribed_text, False)
                
                # Step 3: Speak the response if TTS is available
                if tts_manager is not None:
                    try:
                        current_persona = chat_client.get_current_persona() if chat_client else "remo"
                        tts_manager.speak_persona_response_async(llm_response, current_persona)
                    except Exception as tts_error:
                        logger.warning(f"TTS error in speak-and-chat: {tts_error}")
                
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

@app.route('/personas', methods=['GET'])
def get_personas():
    """Get available personas."""
    try:
        if chat_client is None:
            init_services()
        
        if chat_client is None:
            return jsonify({"error": "Chat service not available"}), 503
        
        personas = chat_client.get_available_personas()
        current_persona = chat_client.get_current_persona()
        
        return jsonify({
            "success": True,
            "personas": personas,
            "current_persona": current_persona
        })
    
    except Exception as e:
        logger.error(f"Error getting personas: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/personas/<persona_name>', methods=['POST'])
def set_persona(persona_name):
    """Set the current persona."""
    try:
        if chat_client is None:
            init_services()
        
        if chat_client is None:
            return jsonify({"error": "Chat service not available"}), 503
        
        if chat_client.set_persona(persona_name):
            return jsonify({
                "success": True,
                "message": f"Persona changed to {persona_name}",
                "current_persona": persona_name
            })
        else:
            return jsonify({"error": f"Persona '{persona_name}' not found"}), 404
    
    except Exception as e:
        logger.error(f"Error setting persona: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/personas/current', methods=['GET'])
def get_current_persona():
    """Get the current persona."""
    try:
        if chat_client is None:
            init_services()
        
        if chat_client is None:
            return jsonify({"error": "Chat service not available"}), 503
        
        current_persona = chat_client.get_current_persona()
        persona_info = chat_client.persona_manager.get_current_persona()
        
        return jsonify({
            "success": True,
            "current_persona": current_persona,
            "persona_info": persona_info
        })
    
    except Exception as e:
        logger.error(f"Error getting current persona: {e}")
        return jsonify({"error": str(e)}), 500

# TTS Endpoints
@app.route('/tts/speak', methods=['POST'])
def tts_speak():
    """Speak text using current or specified persona"""
    try:
        if tts_manager is None:
            return jsonify({"error": "TTS service not available"}), 503
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        
        text = data['text']
        persona = data.get('persona')
        blocking = data.get('blocking', False)
        
        if not text.strip():
            return jsonify({"error": "Empty text provided"}), 400
        
        success = tts_manager.speak_persona_response(text, persona, blocking)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Speech started successfully",
                "persona": persona or tts_manager.current_persona,
                "blocking": blocking
            })
        else:
            return jsonify({"error": "Failed to start speech"}), 500
    
    except Exception as e:
        logger.error(f"Error in TTS speak endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/tts/speak-async', methods=['POST'])
def tts_speak_async():
    """Speak text asynchronously"""
    try:
        if tts_manager is None:
            return jsonify({"error": "TTS service not available"}), 503
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        
        text = data['text']
        persona = data.get('persona')
        
        if not text.strip():
            return jsonify({"error": "Empty text provided"}), 400
        
        success = tts_manager.speak_persona_response_async(text, persona)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Speech started asynchronously",
                "persona": persona or tts_manager.current_persona
            })
        else:
            return jsonify({"error": "Failed to start speech"}), 500
    
    except Exception as e:
        logger.error(f"Error in TTS speak-async endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/tts/stop', methods=['POST'])
def tts_stop():
    """Stop current speech"""
    try:
        if tts_manager is None:
            return jsonify({"error": "TTS service not available"}), 503
        
        tts_manager.stop_speaking()
        return jsonify({
            "success": True,
            "message": "Speech stopped"
        })
    
    except Exception as e:
        logger.error(f"Error stopping TTS: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/tts/set-persona', methods=['POST'])
def tts_set_persona():
    """Set TTS voice for a specific persona"""
    try:
        if tts_manager is None:
            return jsonify({"error": "TTS service not available"}), 503
        
        data = request.get_json()
        if not data or 'persona' not in data:
            return jsonify({"error": "No persona provided"}), 400
        
        persona = data['persona']
        success = tts_manager.set_persona(persona)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"TTS voice set for persona '{persona}'",
                "persona": persona
            })
        else:
            return jsonify({"error": f"Unknown persona: {persona}"}), 400
    
    except Exception as e:
        logger.error(f"Error setting TTS persona: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/tts/status', methods=['GET'])
def tts_status():
    """Get TTS service status"""
    try:
        if tts_manager is None:
            return jsonify({
                "success": True,
                "status": {
                    "available": False,
                    "message": "TTS service not initialized"
                }
            })
        
        status = tts_manager.get_status()
        return jsonify({
            "success": True,
            "status": status
        })
    
    except Exception as e:
        logger.error(f"Error getting TTS status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/tts/enable', methods=['POST'])
def tts_enable():
    """Enable TTS functionality"""
    try:
        if tts_manager is None:
            return jsonify({"error": "TTS service not available"}), 503
        
        tts_manager.enable()
        return jsonify({
            "success": True,
            "message": "TTS enabled"
        })
    
    except Exception as e:
        logger.error(f"Error enabling TTS: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/tts/disable', methods=['POST'])
def tts_disable():
    """Disable TTS functionality"""
    try:
        if tts_manager is None:
            return jsonify({"error": "TTS service not available"}), 503
        
        tts_manager.disable()
        return jsonify({
            "success": True,
            "message": "TTS disabled"
        })
    
    except Exception as e:
        logger.error(f"Error disabling TTS: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        # Handle Windows encoding issues
        import sys
        if sys.platform == "win32":
            import codecs
            import io
            # Only detach if not already detached
            if hasattr(sys.stdout, 'detach'):
                try:
                    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
                except (ValueError, OSError):
                    # Already detached or not detachable
                    pass
            if hasattr(sys.stderr, 'detach'):
                try:
                    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
                except (ValueError, OSError):
                    # Already detached or not detachable
                    pass
        
        print("Starting Remo AI Unified API Server...")
        print("=" * 50)
        
        # Initialize services on startup
        print("Initializing services...")
        init_services()
        
        print("Services initialized")
        print("Starting server on http://localhost:8000")
        print("Available endpoints:")
        print("   - GET  /health - Health check")
        print("   - POST /chat - Send text message")
        print("   - POST /transcribe - Transcribe audio file")
        print("   - POST /speak-and-chat - Complete voice workflow")
        print("   - GET  /personas - Get available personas")
        print("   - POST /personas/<name> - Set persona")
        print("   - GET  /personas/current - Get current persona")
        print("   - POST /tts/speak - Speak text with TTS")
        print("   - POST /tts/speak-async - Speak text asynchronously")
        print("   - POST /tts/stop - Stop current speech")
        print("   - GET  /tts/status - Get TTS service status")
        print("=" * 50)
        
        logger.info("Starting unified API server on port 8000")
        app.run(host='0.0.0.0', port=8000, debug=True)
    except Exception as e:
        print(f"Failed to start server: {e}")
        logger.error(f"Failed to start unified API server: {e}")
        sys.exit(1)
