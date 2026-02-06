# Implements: T014
# Phase III - AI-Powered Todo Chatbot
# Qwen Client - DashScope (Alibaba Cloud) API wrapper with retry logic

import os
import logging
import requests
from typing import List, Dict, Any, Optional
import random


logger = logging.getLogger(__name__)


class QwenClient:
    """
    DashScope Qwen model client with retry logic and timeout handling.

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
        self.model = model or os.getenv("QWEN_MODEL", "qwen-turbo")
        self.timeout = timeout
        self.max_retries = max_retries
        self.api_key = os.getenv("DASHSCOPE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "DASHSCOPE_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )

        self.api_base = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

        logger.info(f"Qwen client initialized with model: {self.model}, timeout: {timeout}s")

    def generate(
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
        import time

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Qwen inference attempt {attempt + 1}/{self.max_retries}")

                # Build DashScope API request
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                # Convert OpenAI format to DashScope format
                input_messages = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")

                    # Map OpenAI roles to DashScope roles
                    if role == "system":
                        dashscope_role = "system"
                    elif role == "user":
                        dashscope_role = "user"
                    elif role == "assistant":
                        dashscope_role = "assistant"
                    else:
                        dashscope_role = "user"

                    input_messages.append({
                        "role": dashscope_role,
                        "content": content
                    })

                payload = {
                    "model": self.model,
                    "input": {
                        "messages": input_messages
                    },
                    "parameters": {
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "result_format": "message"
                    }
                }

                # Call DashScope API
                response = requests.post(
                    self.api_base,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )

                response.raise_for_status()
                result = response.json()

                # Extract generated text from response
                if "output" in result and "choices" in result["output"]:
                    generated_text = result["output"]["choices"][0]["message"]["content"]
                    logger.info("Qwen inference successful")
                    return generated_text.strip()
                else:
                    raise ValueError(f"Unexpected response format: {result}")

            except Exception as e:
                logger.error(f"Qwen inference failed on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise

                # Check if it's a rate limit error (HTTP 429)
                if "429" in str(e) or "rate limit" in str(e).lower():
                    logger.warning("Rate limit detected, waiting 60 seconds...")
                    time.sleep(60)
                else:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
