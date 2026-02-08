"""
HuggingFace AI Client for Todo App

Provides integration with HuggingFace Inference API for AI-powered todo management.
"""
import os
import json
import logging
from typing import Optional, List, Dict, Any
import requests

from src.core.config import settings

logger = logging.getLogger(__name__)


class HuggingFaceClient:
    """Client for HuggingFace Inference API"""

    def __init__(
        self,
        model: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize HuggingFace client with API key and model

        Args:
            model: Model name (from env or default)
            timeout: Request timeout in seconds
        """
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable is required")

        self.model = model or os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        self.timeout = timeout
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"

        logger.info(f"HuggingFace client initialized with model: {self.model}")

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate response from HuggingFace AI (compatible with QwenClient interface)

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            AI-generated response text
        """
        try:
            # Build prompt from messages
            prompt = self._build_prompt(messages)

            # Prepare request payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens,
                    "return_full_text": False
                }
            }

            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Parse response
            result = response.json()

            # Handle different response formats
            if isinstance(result, list):
                if len(result) > 0 and isinstance(result[0], dict):
                    if "generated_text" in result[0]:
                        return result[0]["generated_text"].strip()
            elif isinstance(result, dict):
                if "generated_text" in result:
                    return result["generated_text"].strip()

            logger.warning(f"Unexpected response format: {result}")
            return "I apologize, but I couldn't generate a proper response. Please try again."

        except requests.exceptions.HTTPError as e:
            logger.error(f"HuggingFace API HTTP error: {e.response.status_code} - {e.response.text}")

            if e.response.status_code == 429:
                return "I'm currently experiencing high demand. Please wait a moment and try again."
            elif e.response.status_code == 401:
                return "API authentication failed. Please check the API key."
            elif e.response.status_code == 503:
                return "The AI model is loading. Please wait a moment and try again."
            else:
                return f"API error occurred: {e.response.status_code}"

        except requests.exceptions.RequestException as e:
            logger.error(f"HuggingFace API request error: {str(e)}")
            return "I'm having trouble connecting to my AI services. Please check your connection and try again."

        except Exception as e:
            logger.error(f"Unexpected error in HuggingFace client: {str(e)}", exc_info=True)
            return "An unexpected error occurred. Please try again."

    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Build a prompt from messages in OpenAI format

        Args:
            messages: List of message dicts with 'role' and 'content' keys

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        return "\n\n".join(prompt_parts) + "\n\nAssistant:"

    async def health_check(self) -> bool:
        """Check if HuggingFace API is accessible"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": "Hello",
                "parameters": {"max_new_tokens": 10}
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10.0
            )
            return response.status_code == 200

        except Exception as e:
            logger.error(f"HuggingFace health check failed: {str(e)}")
            return False
