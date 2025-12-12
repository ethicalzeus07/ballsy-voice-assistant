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

logger = logging.getLogger(__name__)

# Read environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
# Try different TTS model names - some may not be available yet
GEMINI_TTS_MODEL = os.getenv("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")  # Try preview version
GEMINI_TTS_VOICE = os.getenv("GEMINI_TTS_VOICE", "Kore")

# Initialize Gemini client
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not configured for TTS")
    client = None
else:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info(f"Gemini TTS client initialized with model={GEMINI_TTS_MODEL}, voice={GEMINI_TTS_VOICE}")
    except Exception as e:
        logger.error(f"Failed to create Gemini TTS client: {e}")
        client = None


def synthesize_pcm(text: str) -> bytes:
    """
    Return raw PCM audio bytes for the given text using Gemini TTS.
    
    Args:
        text: Text to convert to speech
    
    Returns:
        Raw PCM audio bytes
    
    Raises:
        ValueError: If GEMINI_API_KEY is not configured
        Exception: If TTS synthesis fails
    """
    if not client:
        raise ValueError("GEMINI_API_KEY not configured for TTS")
    
    if not text or not text.strip():
        logger.warning("Empty text provided for TTS")
        raise ValueError("Empty text provided for TTS")
    
    try:
        logger.info(f"Synthesizing speech: '{text[:50]}...' with voice '{GEMINI_TTS_VOICE}' using model '{GEMINI_TTS_MODEL}'")
        
        # Try multiple TTS models in order of preference
        # Note: TTS models may have different names or may not be available yet
        tts_models = [
            GEMINI_TTS_MODEL,
            "gemini-2.5-flash-preview-tts",
            "gemini-2.5-flash-tts",
            "gemini-2.5-pro-preview-tts",
        ]
        
        resp = None
        last_error = None
        for model_name in tts_models:
            try:
                logger.info(f"Trying TTS model: {model_name}")
                # Generate audio using Gemini TTS with proper configuration
                resp = client.models.generate_content(
                    model=model_name,
                    contents=text,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=GEMINI_TTS_VOICE
                                )
                            )
                        ),
                    ),
                )
                # If we get here, the model worked
                logger.info(f"✅ Successfully used TTS model: {model_name}")
                break
            except Exception as model_error:
                error_str = str(model_error).lower()
                if '404' in error_str or 'not found' in error_str or 'not supported' in error_str:
                    logger.warning(f"Model {model_name} not found/supported: {str(model_error)[:100]}")
                    last_error = model_error
                    continue
                # For other errors, raise immediately
                logger.error(f"Non-404 error with model {model_name}: {model_error}")
                raise
        
        # Check if we got a valid response
        if resp is None:
            error_msg = f"No TTS models available. Last error: {str(last_error)[:200] if last_error else 'Unknown'}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Extract PCM data from response: first candidate, first part, inline_data.data
        if resp and hasattr(resp, 'candidates') and resp.candidates:
            candidate = resp.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                if candidate.content.parts and len(candidate.content.parts) > 0:
                    part = candidate.content.parts[0]
                    if hasattr(part, 'inline_data') and hasattr(part.inline_data, 'data'):
                        # The data is already base64-encoded PCM bytes
                        audio_data_b64 = part.inline_data.data
                        # Decode base64 to get raw PCM bytes
                        audio_bytes = base64.b64decode(audio_data_b64)
                        logger.info(f"✅ Successfully synthesized speech (length: {len(audio_bytes)} bytes)")
                        return audio_bytes
        
        logger.warning("Could not extract audio data from TTS response")
        raise ValueError("Could not extract audio data from TTS response")
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}", exc_info=True)
        raise


def synthesize_speech_base64(text: str) -> Optional[str]:
    """
    Synthesize speech and return as base64-encoded string for easy transmission.
    
    Args:
        text: Text to convert to speech
    
    Returns:
        Base64-encoded audio string, or None if synthesis fails
    """
    try:
        audio_bytes = synthesize_pcm(text)
        if audio_bytes:
            return base64.b64encode(audio_bytes).decode('utf-8')
        return None
    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")
        return None
