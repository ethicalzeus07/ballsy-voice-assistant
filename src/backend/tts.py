"""
Gemini Text-to-Speech (TTS) integration for Ballsy Voice Assistant.
Uses Google Gemini TTS API for natural, human-like voice synthesis.
"""

import os
import base64
import logging
from typing import Optional
from google import genai
from google.genai import types
from src.backend.config import config

logger = logging.getLogger(__name__)

# Initialize Gemini client for TTS
_tts_client = None

# Available Gemini TTS voices (prebuilt voices)
AVAILABLE_VOICES = [
    "Kore",      # Default - natural, clear voice
    "Aoede",    # Alternative voice option
    "Puck",      # Alternative voice option
    "Charon",    # Alternative voice option
    "Fenrir",   # Alternative voice option
    "Kore-hi",   # Hindi variant
    "Aoede-es", # Spanish variant
]

# Default TTS model
DEFAULT_TTS_MODEL = "gemini-2.5-flash-tts"


def _get_tts_client():
    """Get or create the Gemini TTS client."""
    global _tts_client
    if _tts_client is None:
        api_key = config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            logger.error("GEMINI_API_KEY not configured for TTS")
            raise ValueError("GEMINI_API_KEY not configured")
        try:
            _tts_client = genai.Client(api_key=api_key)
            logger.info("Gemini TTS client initialized")
        except Exception as e:
            logger.error(f"Failed to create Gemini TTS client: {e}")
            raise
    return _tts_client


def synthesize_speech(
    text: str,
    voice_name: str = "Kore",
    model: Optional[str] = None
) -> Optional[bytes]:
    """
    Synthesize speech from text using Gemini TTS.
    
    Args:
        text: Text to convert to speech
        voice_name: Prebuilt voice name (default: "Kore")
        model: TTS model name (default: gemini-2.5-flash-tts)
    
    Returns:
        Raw PCM audio bytes, or None if synthesis fails
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for TTS")
        return None
    
    try:
        client = _get_tts_client()
        tts_model = model or os.getenv("GEMINI_TTS_MODEL", DEFAULT_TTS_MODEL)
        
        logger.debug(f"Synthesizing speech: '{text[:50]}...' with voice '{voice_name}' using model '{tts_model}'")
        
        # Generate audio using Gemini TTS
        response = client.models.generate_content(
            model=tts_model,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                ),
            ),
        )
        
        # Extract audio data from response
        if response and hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                if candidate.content.parts and len(candidate.content.parts) > 0:
                    part = candidate.content.parts[0]
                    if hasattr(part, 'inline_data') and hasattr(part.inline_data, 'data'):
                        # Decode base64 audio data
                        audio_data_b64 = part.inline_data.data
                        audio_bytes = base64.b64decode(audio_data_b64)
                        logger.info(f"✅ Successfully synthesized speech (length: {len(audio_bytes)} bytes)")
                        return audio_bytes
        
        logger.warning("Could not extract audio data from TTS response")
        return None
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}", exc_info=True)
        return None


def synthesize_speech_base64(
    text: str,
    voice_name: str = "Kore",
    model: Optional[str] = None
) -> Optional[str]:
    """
    Synthesize speech and return as base64-encoded string for easy transmission.
    
    Args:
        text: Text to convert to speech
        voice_name: Prebuilt voice name (default: "Kore")
        model: TTS model name (default: gemini-2.5-flash-tts)
    
    Returns:
        Base64-encoded audio string, or None if synthesis fails
    """
    audio_bytes = synthesize_speech(text, voice_name, model)
    if audio_bytes:
        return base64.b64encode(audio_bytes).decode('utf-8')
    return None
