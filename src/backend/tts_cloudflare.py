"""
Cloudflare Workers AI Text-to-Speech integration.
Uses the hosted @cf/myshell-ai/melotts model and returns base64 MP3 audio.
"""

import logging
from typing import Optional

import requests

from src.backend.config import config

logger = logging.getLogger(__name__)


def _model_url() -> str:
    model = config.CLOUDFLARE_TTS_MODEL.lstrip("/")
    return (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{config.CLOUDFLARE_ACCOUNT_ID}/ai/run/{model}"
    )


def synthesize_cloudflare_tts_base64(text: str) -> Optional[str]:
    """
    Synthesize text with Cloudflare Workers AI TTS.

    Returns:
        Base64-encoded MP3 audio, or None if synthesis is unavailable/fails.
    """
    if not config.USE_CLOUDFLARE_TTS:
        return None

    if not config.CLOUDFLARE_ACCOUNT_ID or not config.CLOUDFLARE_API_TOKEN:
        logger.warning("Cloudflare TTS enabled but CLOUDFLARE_ACCOUNT_ID/API_TOKEN is missing")
        return None

    text = (text or "").strip()
    if not text:
        return None

    try:
        response = requests.post(
            _model_url(),
            headers={
                "Authorization": f"Bearer {config.CLOUDFLARE_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "prompt": text,
                "lang": config.CLOUDFLARE_TTS_LANG,
            },
            timeout=30,
        )
        if response.status_code >= 400:
            logger.error(
                "Cloudflare TTS error %s: %s",
                response.status_code,
                response.text[:500],
            )
            return None

        data = response.json()
        result = data.get("result") or {}
        audio = result.get("audio") if isinstance(result, dict) else None
        if not audio:
            logger.warning("Cloudflare TTS returned no audio")
            return None

        logger.info("Generated Cloudflare TTS audio (length: %s chars)", len(audio))
        return audio
    except Exception as e:
        logger.warning("Cloudflare TTS failed: %s", e)
        return None
