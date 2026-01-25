# Implements: T014
# Phase III - AI-Powered Todo Chatbot
# Qwen Client - Hugging Face SDK wrapper with retry logic

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
import random

from huggingface_hub import AsyncInferenceClient


logger = logging.getLogger(__name__)


class QwenClient:
    """
    Hugging Face Qwen model client with retry logic and timeout handling.

    Implements exponential backoff retry strategy for transient failures.
    """

    def __init__(
        self,
        model: str = None,
        timeout: int = 8,
        max_retries: int = 3
    ):
        """
        Initialize Qwen client.

        Args:
            model: Qwen model name (from env or default)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.model = model or os.getenv("QWEN_MODEL", "Qwen/Qwen-14B-Chat")
        self.timeout = timeout
        self.max_retries = max_retries
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "HUGGINGFACE_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )

        # Initialize async inference client
        self.client = AsyncInferenceClient(model=self.model, token=self.api_key)

        logger.info(f"Qwen client initialized with model: {self.model}, timeout: {timeout}s")

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate response from Qwen model with retry logic.

        Args:
            messages: Chat messages array (OpenAI format)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response

        Raises:
            Exception: If all retries exhausted
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Qwen inference attempt {attempt + 1}/{self.max_retries}")

                # Build prompt from messages
                prompt = self._build_prompt(messages)

                # Call Hugging Face API with timeout
                response = await asyncio.wait_for(
                    self.client.text_generation(
                        prompt=prompt,
                        temperature=temperature,
                        max_new_tokens=max_tokens,
                        do_sample=True
                    ),
                    timeout=self.timeout
                )

                logger.info("Qwen inference successful")
                return response.strip()

            except asyncio.TimeoutError:
                logger.warning(f"Qwen inference timeout on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    raise TimeoutError(f"Qwen inference timed out after {self.max_retries} attempts")
                # Exponential backoff with jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.info(f"Retrying in {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f"Qwen inference failed on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise

                # Check if it's a rate limit error (HTTP 429)
                if "429" in str(e) or "rate limit" in str(e).lower():
                    logger.warning("Rate limit detected, waiting 60 seconds...")
                    await asyncio.sleep(60)
                else:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {wait_time:.2f}s...")
                    await asyncio.sleep(wait_time)

    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Build prompt from message array for Qwen.

        Args:
            messages: Chat messages in OpenAI format

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

        prompt = "\n".join(prompt_parts)
        prompt += "\nAssistant:"

        return prompt
