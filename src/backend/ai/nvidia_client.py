"""
NVIDIA NIM AI client for Ballsy Voice Assistant.
Uses NVIDIA's OpenAI-compatible chat completions endpoint.
"""

import asyncio
import logging
from typing import Dict, List, Optional

import requests

from src.backend.config import config

logger = logging.getLogger(__name__)


def _chat_completions_url() -> str:
    """Return the configured NVIDIA chat completions URL."""
    base_url = config.NVIDIA_BASE_URL.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


async def generate_reply(
    prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    temperature: float = 0.5,
    max_tokens: int = 75,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Generate a reply using NVIDIA NIM's OpenAI-compatible API.

    Args:
        prompt: User's prompt/question.
        conversation_history: Previous messages as [{"role": "user|assistant", "content": "..."}].
        temperature: Sampling temperature.
        max_tokens: Maximum generated tokens.
        system_prompt: System prompt/instructions.

    Returns:
        Generated response text.
    """
    if not config.NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY not configured")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if conversation_history:
        for msg in conversation_history[-6:]:
            role = "assistant" if msg.get("role") == "assistant" else "user"
            content = str(msg.get("content", "")).strip()
            if content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": config.NVIDIA_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {config.NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }

    def _request() -> str:
        response = requests.post(
            _chat_completions_url(),
            headers=headers,
            json=payload,
            timeout=45,
        )
        if response.status_code >= 400:
            logger.error("NVIDIA API error %s: %s", response.status_code, response.text[:500])
            response.raise_for_status()

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise ValueError("NVIDIA API returned no choices")

        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )

        text = str(content).strip()
        if not text:
            raise ValueError("NVIDIA API returned an empty response")
        return text

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _request)


async def generate_reply_simple(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Generate a reply without conversation history."""
    return await generate_reply(prompt, conversation_history=None, system_prompt=system_prompt)
