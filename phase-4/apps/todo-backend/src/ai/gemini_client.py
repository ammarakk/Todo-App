"""
Google Gemini AI Client for Todo App

Provides integration with Google's Gemini API for AI-powered todo management.
"""
import os
import json
from typing import Optional, Dict, Any
from logging import getLogger
import httpx

from src.core.config import settings

logger = getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client with API key"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        self.timeout = 30.0

    def generate(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate response from Gemini AI (compatible with QwenClient interface)

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            AI-generated response text
        """
        import asyncio

        # Run async method in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self._generate_async(messages, temperature, max_tokens)
        )

    async def _generate_async(
        self,
        messages: list,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Async implementation of generate method"""
        try:
            # Build the contents array with conversation history
            contents = []

            # Convert messages format to Gemini format
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                # Map OpenAI roles to Gemini roles
                if role == "system":
                    # Gemini doesn't have system role, prepend as user message
                    contents.append({
                        "role": "user",
                        "parts": [{"text": f"System: {content}"}]
                    })
                elif role == "user":
                    contents.append({
                        "role": "user",
                        "parts": [{"text": content}]
                    })
                elif role == "assistant":
                    contents.append({
                        "role": "model",
                        "parts": [{"text": content}]
                    })

            # Prepare request payload
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": max_tokens,
                }
            }

            # Make API request
            url = f"{self.base_url}?key={self.api_key}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()

            # Extract the response text
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]

            logger.warning("Empty or invalid response from Gemini API")
            return "I apologize, but I couldn't generate a response. Please try again."

        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                return "I'm currently experiencing high demand. Please wait a moment and try again."
            elif e.response.status_code == 400:
                return "I couldn't process that request. Please rephrase and try again."
            else:
                return f"API error occurred: {e.response.status_code}"

        except httpx.RequestError as e:
            logger.error(f"Gemini API request error: {str(e)}")
            return "I'm having trouble connecting to my AI services. Please check your connection and try again."

        except Exception as e:
            logger.error(f"Unexpected error in Gemini client: {str(e)}", exc_info=True)
            return "An unexpected error occurred. Please try again."

    async def generate_response(
        self,
        message: str,
        conversation_history: Optional[list] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response from Gemini AI

        Args:
            message: User's message
            conversation_history: Optional list of previous messages
            system_prompt: Optional system prompt to guide AI behavior

        Returns:
            AI-generated response text
        """
        try:
            # Build the contents array with conversation history
            contents = []

            # Add system prompt if provided
            if system_prompt:
                contents.append({
                    "role": "user",
                    "parts": [{"text": system_prompt}]
                })

            # Add conversation history
            if conversation_history:
                for hist_item in conversation_history:
                    role = "user" if hist_item.get("role") == "user" else "model"
                    contents.append({
                        "role": role,
                        "parts": [{"text": hist_item.get("content", "")}]
                    })

            # Add current message
            contents.append({
                "role": "user",
                "parts": [{"text": message}]
            })

            # Prepare request payload
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }

            # Make API request
            url = f"{self.base_url}?key={self.api_key}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()

            # Extract the response text
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]

            logger.warning("Empty or invalid response from Gemini API")
            return "I apologize, but I couldn't generate a response. Please try again."

        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                return "I'm currently experiencing high demand. Please wait a moment and try again."
            elif e.response.status_code == 400:
                return "I couldn't process that request. Please rephrase and try again."
            else:
                return f"API error occurred: {e.response.status_code}"

        except httpx.RequestError as e:
            logger.error(f"Gemini API request error: {str(e)}")
            return "I'm having trouble connecting to my AI services. Please check your connection and try again."

        except Exception as e:
            logger.error(f"Unexpected error in Gemini client: {str(e)}", exc_info=True)
            return "An unexpected error occurred. Please try again."

    async def health_check(self) -> bool:
        """Check if Gemini API is accessible"""
        try:
            url = f"{self.base_url}?key={self.api_key}"
            payload = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": "Hello"}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 10
                }
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                return response.status_code == 200

        except Exception as e:
            logger.error(f"Gemini health check failed: {str(e)}")
            return False
