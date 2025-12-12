"""
Google Cloud Text-to-Speech integration for Ballsy Voice Assistant.
Uses Google Cloud Text-to-Speech API (WaveNet/Neural2 voices) for high-quality, human-like voice synthesis.

This module uses Application Default Credentials (ADC) on Cloud Run, so no API keys are needed.
The Cloud Run service account must have the 'cloudtexttospeech.user' role.
"""

import logging
from typing import Optional
from google.cloud import texttospeech

logger = logging.getLogger(__name__)

# Initialize client (uses ADC on Cloud Run automatically)
try:
    client = texttospeech.TextToSpeechClient()
    logger.info("Google Cloud Text-to-Speech client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Google Cloud TTS client: {e}")
    client = None


def synthesize_tts(
    text: str,
    language_code: str = "en-US",
    voice_name: str = "en-US-Neural2-A",
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
    audio_encoding: texttospeech.AudioEncoding = texttospeech.AudioEncoding.MP3,
) -> bytes:
    """
    Synthesize text to speech using Google Cloud Text-to-Speech and return raw audio bytes.
    
    Args:
        text: Text to convert to speech
        language_code: Language code (e.g., "en-US")
        voice_name: Voice name (e.g., "en-US-Neural2-A" for very natural voice)
        speaking_rate: Speaking rate (0.25 to 4.0, default 1.0)
        pitch: Pitch adjustment (-20.0 to 20.0 semitones, default 0.0)
        audio_encoding: Audio encoding format (MP3, OGG_OPUS, etc.)
    
    Returns:
        Raw audio bytes
    
    Raises:
        ValueError: If client is not initialized or text is empty
        Exception: If TTS synthesis fails
    """
    if not client:
        raise ValueError("Google Cloud TTS client not initialized. Check service account permissions.")
    
    if not text or not text.strip():
        logger.warning("Empty text provided for TTS")
        raise ValueError("Empty text provided for TTS")
    
    try:
        logger.debug(f"Synthesizing speech: '{text[:50]}...' with voice '{voice_name}'")
        
        # Create synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Configure voice selection
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
        )
        
        # Configure audio settings
        audio_config = texttospeech.AudioConfig(
            audio_encoding=audio_encoding,
            speaking_rate=speaking_rate,
            pitch=pitch,
        )
        
        # Synthesize speech
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
        
        logger.info(f"✅ Successfully synthesized speech (length: {len(response.audio_content)} bytes)")
        return response.audio_content
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}", exc_info=True)
        raise


def synthesize_tts_base64(
    text: str,
    language_code: str = "en-US",
    voice_name: str = "en-US-Neural2-A",
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
    audio_encoding: texttospeech.AudioEncoding = texttospeech.AudioEncoding.MP3,
) -> Optional[str]:
    """
    Synthesize speech and return as base64-encoded string for easy transmission.
    
    Args:
        text: Text to convert to speech
        language_code: Language code (e.g., "en-US")
        voice_name: Voice name (e.g., "en-US-Neural2-A")
        speaking_rate: Speaking rate (0.25 to 4.0)
        pitch: Pitch adjustment (-20.0 to 20.0 semitones)
        audio_encoding: Audio encoding format
    
    Returns:
        Base64-encoded audio string, or None if synthesis fails
    """
    import base64
    try:
        audio_bytes = synthesize_tts(
            text=text,
            language_code=language_code,
            voice_name=voice_name,
            speaking_rate=speaking_rate,
            pitch=pitch,
            audio_encoding=audio_encoding,
        )
        if audio_bytes:
            return base64.b64encode(audio_bytes).decode('utf-8')
        return None
    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")
        return None
