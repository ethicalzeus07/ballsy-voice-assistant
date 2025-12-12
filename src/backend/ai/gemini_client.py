"""
Gemini AI client for Ballsy Voice Assistant.
Uses the Google GenAI SDK (google-genai) for the Gemini Developer API.
"""

import os
import logging
import asyncio
from typing import List, Dict, Optional
from google import genai
from google.genai import types
from src.backend.config import config

logger = logging.getLogger(__name__)

# Initialize Gemini client
_client = None


def _get_client():
    """Get or create the Gemini client."""
    global _client
    if _client is None:
        # Try to get API key from config, fallback to environment variables
        # The SDK can use either GEMINI_API_KEY or GOOGLE_API_KEY
        api_key = config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            logger.error("GEMINI_API_KEY not configured in config or environment")
            raise ValueError("GEMINI_API_KEY not configured")
        # Log first few chars for debugging (don't log full key)
        logger.info(f"Initializing Gemini client with API key (starts with: {api_key[:10]}...)")
        try:
            _client = genai.Client(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to create Gemini client: {e}")
            raise
    return _client


async def generate_reply(
    prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    temperature: float = 0.5,
    max_tokens: int = 75,
    system_prompt: Optional[str] = None
) -> str:
    """
    Generate a reply using Gemini API.
    
    Args:
        prompt: User's prompt/question
        conversation_history: List of previous messages in format [{"role": "user|assistant", "content": "..."}]
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens in response
        system_prompt: System prompt/instructions
    
    Returns:
        Generated response text
    
    Raises:
        Exception: If API call fails
    """
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    try:
        client = _get_client()
        
        # Build the full prompt with system prompt and history
        full_prompt_parts = []
        
        # Add system prompt if provided
        if system_prompt:
            full_prompt_parts.append(f"System instructions: {system_prompt}\n\n")
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                role_label = "User" if msg["role"] == "user" else "Assistant"
                full_prompt_parts.append(f"{role_label}: {msg['content']}\n")
        
        # Add current user prompt
        full_prompt_parts.append(f"User: {prompt}\nAssistant:")
        
        full_prompt = "".join(full_prompt_parts)
        
        # Use a cheap Flash model - try multiple models in order
        # Based on API availability, try these models
        model_names = [
            getattr(config, 'GEMINI_MODEL', 'gemini-2.0-flash-exp'),
            'gemini-2.0-flash-exp',  # This was working in logs
            'gemini-2.5-flash',
            'gemini-2.5-flash-lite',
            'gemini-2.0-flash',
        ]
        
        # Generate content (Gemini API is synchronous, so we run it in executor)
        loop = asyncio.get_event_loop()
        
        # Use the correct API format for google-genai SDK
        def _generate():
            last_error = None
            for model_name in model_names:
                try:
                    # Create config object
                    gen_config = types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    )
                    logger.debug(f"Trying model: {model_name}")
                    return client.models.generate_content(
                        model=model_name,
                        contents=full_prompt,
                        config=gen_config,
                    )
                except Exception as e:
                    error_str = str(e).lower()
                    # Check if it's a model not found error
                    if any(x in error_str for x in ['404', 'not found', 'not supported', 'not_found']):
                        logger.warning(f"Model {model_name} not found (error: {str(e)[:100]}), trying next model...")
                        last_error = e
                        continue
                    # For other errors (like API key issues), log and raise
                    logger.error(f"Non-404 error with model {model_name}: {e}")
                    raise
            
            # If all models failed, raise the last error
            if last_error:
                raise last_error
            raise Exception("No models available")
        
        response = await loop.run_in_executor(None, _generate)
        
        # Extract text from response
        # According to google-genai SDK docs: response.text should work directly
        if response is None:
            logger.error("Gemini API returned None response")
            return "I'm having trouble generating a response. Please try again."
        
        try:
            # Log response type for debugging
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response class: {response.__class__.__name__}")
            
            # The google-genai SDK might return the response wrapped or directly
            # Try multiple extraction methods
            
            # Method 1: Direct .text property (SDK documentation says this should work)
            try:
                if hasattr(response, 'text'):
                    text_value = response.text
                    logger.info(f"response.text exists, type: {type(text_value)}, value preview: {repr(str(text_value)[:50]) if text_value else 'None'}")
                    if text_value is not None and str(text_value).strip():
                        text_str = str(text_value).strip()
                        logger.info(f"✅ Successfully extracted text via .text (length: {len(text_str)})")
                        return text_str
                    else:
                        logger.warning(f"response.text returned empty/None: {text_value}")
            except Exception as e:
                logger.warning(f"Error accessing response.text: {e}")
            
            # Method 2: Check if response has a parsed/parsed_response attribute
            try:
                if hasattr(response, 'parsed'):
                    parsed = response.parsed
                    logger.info(f"Found parsed attribute: {type(parsed)}")
                    if hasattr(parsed, 'text') and parsed.text:
                        text_str = str(parsed.text).strip()
                        logger.info(f"✅ Extracted text via parsed.text (length: {len(text_str)})")
                        return text_str
            except Exception as e:
                logger.debug(f"parsed access failed: {e}")
            
            # Method 3: Try .candidates[0].content.parts[0].text
            try:
                candidates = None
                if hasattr(response, 'candidates'):
                    candidates = response.candidates
                elif hasattr(response, 'parsed') and hasattr(response.parsed, 'candidates'):
                    candidates = response.parsed.candidates
                
                if candidates and len(candidates) > 0:
                    candidate = candidates[0]
                    logger.info(f"Found candidate: {type(candidate)}")
                    if hasattr(candidate, 'content'):
                        content = candidate.content
                        if hasattr(content, 'parts') and content.parts and len(content.parts) > 0:
                            part = content.parts[0]
                            logger.info(f"Found part: {type(part)}")
                            if hasattr(part, 'text'):
                                text_value = part.text
                                if text_value:
                                    text_str = str(text_value).strip()
                                    logger.info(f"✅ Extracted text via candidates[0].content.parts[0].text (length: {len(text_str)})")
                                    return text_str
            except Exception as e:
                logger.warning(f"candidates access failed: {e}", exc_info=True)
            
            # Method 4: Try to get the underlying data
            try:
                # Check if it's a dict-like object
                if hasattr(response, '__dict__'):
                    logger.info(f"Response __dict__ keys: {list(response.__dict__.keys())[:10]}")
                if hasattr(response, 'data'):
                    data = response.data
                    logger.info(f"Found data attribute: {type(data)}")
                    if hasattr(data, 'candidates') or (isinstance(data, dict) and 'candidates' in data):
                        # Try to extract from data
                        pass
            except Exception as e:
                logger.debug(f"data access failed: {e}")
            
            # Log detailed response info for debugging
            logger.error(f"❌ Could not extract text. Response type: {type(response)}")
            attrs = [a for a in dir(response) if not a.startswith('_')]
            logger.error(f"Response attributes (first 30): {attrs[:30]}")
            
            # Try to inspect what response.text actually contains
            if hasattr(response, 'text'):
                try:
                    text_attr = response.text
                    logger.error(f"response.text type: {type(text_attr)}, value: {repr(text_attr)[:300]}")
                except Exception as e:
                    logger.error(f"Could not access response.text: {e}")
            
            # Log response string representation
            try:
                response_str = str(response)
                if len(response_str) > 50:
                    logger.error(f"Response as string (first 500 chars): {response_str[:500]}")
            except:
                pass
            
        except Exception as parse_error:
            logger.error(f"Error parsing Gemini response: {parse_error}", exc_info=True)
        
        return "I'm having trouble generating a response. Please try again."
            
    except Exception as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        raise


async def generate_reply_simple(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Simplified version that generates a reply without conversation history.
    
    Args:
        prompt: User's prompt
        system_prompt: Optional system instructions
    
    Returns:
        Generated response text
    """
    return await generate_reply(prompt, conversation_history=None, system_prompt=system_prompt)

