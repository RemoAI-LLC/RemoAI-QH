"""
TTS API endpoints for Remo AI
Provides REST API for text-to-speech functionality
"""

import logging
from flask import Blueprint, request, jsonify, send_file
import tempfile
import os
from persona_tts import PersonaTTSManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create TTS blueprint
tts_bp = Blueprint('tts', __name__)

# Initialize TTS manager
tts_manager = PersonaTTSManager()

@tts_bp.route('/tts/speak', methods=['POST'])
def speak_text():
    """
    Speak text using current or specified persona
    
    Expected JSON data:
    - text: Text to speak
    - persona: Persona name (optional)
    - blocking: Whether to wait for completion (optional, default: false)
    """
    try:
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
        logger.error(f"Error in speak endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@tts_bp.route('/tts/speak-async', methods=['POST'])
def speak_text_async():
    """
    Speak text asynchronously
    
    Expected JSON data:
    - text: Text to speak
    - persona: Persona name (optional)
    """
    try:
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
        logger.error(f"Error in speak-async endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@tts_bp.route('/tts/speak-to-file', methods=['POST'])
def speak_to_file():
    """
    Convert text to speech and return audio file
    
    Expected JSON data:
    - text: Text to convert
    - persona: Persona name (optional)
    - format: Audio format (optional, default: wav)
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        
        text = data['text']
        persona = data.get('persona')
        audio_format = data.get('format', 'wav')
        
        if not text.strip():
            return jsonify({"error": "Empty text provided"}), 400
        
        # Set persona if specified
        if persona:
            tts_manager.set_persona(persona)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=f'.{audio_format}', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # Generate speech file
        success = tts_manager.tts_service.speak_to_file(text, temp_filename)
        
        if success and os.path.exists(temp_filename):
            return send_file(
                temp_filename,
                as_attachment=True,
                download_name=f'speech.{audio_format}',
                mimetype='audio/wav' if audio_format == 'wav' else 'audio/mpeg'
            )
        else:
            return jsonify({"error": "Failed to generate speech file"}), 500
    
    except Exception as e:
        logger.error(f"Error in speak-to-file endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@tts_bp.route('/tts/stop', methods=['POST'])
def stop_speech():
    """Stop current speech"""
    try:
        tts_manager.stop_speaking()
        return jsonify({
            "success": True,
            "message": "Speech stopped"
        })
    
    except Exception as e:
        logger.error(f"Error stopping speech: {e}")
        return jsonify({"error": str(e)}), 500

@tts_bp.route('/tts/set-persona', methods=['POST'])
def set_tts_persona():
    """
    Set TTS voice for a specific persona
    
    Expected JSON data:
    - persona: Persona name
    """
    try:
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

@tts_bp.route('/tts/status', methods=['GET'])
def get_tts_status():
    """Get TTS service status"""
    try:
        status = tts_manager.get_status()
        return jsonify({
            "success": True,
            "status": status
        })
    
    except Exception as e:
        logger.error(f"Error getting TTS status: {e}")
        return jsonify({"error": str(e)}), 500

@tts_bp.route('/tts/enable', methods=['POST'])
def enable_tts():
    """Enable TTS functionality"""
    try:
        tts_manager.enable()
        return jsonify({
            "success": True,
            "message": "TTS enabled"
        })
    
    except Exception as e:
        logger.error(f"Error enabling TTS: {e}")
        return jsonify({"error": str(e)}), 500

@tts_bp.route('/tts/disable', methods=['POST'])
def disable_tts():
    """Disable TTS functionality"""
    try:
        tts_manager.disable()
        return jsonify({
            "success": True,
            "message": "TTS disabled"
        })
    
    except Exception as e:
        logger.error(f"Error disabling TTS: {e}")
        return jsonify({"error": str(e)}), 500

@tts_bp.route('/tts/voices', methods=['GET'])
def get_available_voices():
    """Get available TTS voices"""
    try:
        voices = tts_manager.tts_service.supported_voices
        persona_voices = tts_manager.persona_voices
        
        return jsonify({
            "success": True,
            "espeak_voices": voices,
            "persona_voices": persona_voices,
            "current_persona": tts_manager.current_persona
        })
    
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        return jsonify({"error": str(e)}), 500
