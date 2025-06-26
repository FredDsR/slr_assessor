"""Abstraction layer and concrete LLM provider integrations."""

import json
import os
from typing import Protocol, runtime_checkable
from ..models import LLMAssessment


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers."""

    def get_assessment(self, prompt: str) -> str:
        """Get assessment from the LLM provider.

        Args:
            prompt: The formatted prompt to send to the LLM

        Returns:
            Raw response string from the LLM
        """
        ...


class OpenAIProvider:
    """OpenAI GPT provider implementation."""

    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key. If None, reads from environment
            model: Model name to use (default: gpt-4)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided and OPENAI_API_KEY environment variable not set"
            )

        # Import here to make it optional
        try:
            import openai

            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "openai package not installed. Install with: uv pip install openai"
            )

    def get_assessment(self, prompt: str) -> str:
        """Get assessment from OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a research assistant that provides structured JSON responses.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class GeminiProvider:
    """Google Gemini provider implementation."""

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        """Initialize Gemini provider.

        Args:
            api_key: Google API key. If None, reads from environment
            model: Model name to use (default: gemini-1.5-flash)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError(
                "Google API key not provided and GOOGLE_API_KEY environment variable not set"
            )

        # Import here to make it optional
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. Install with: uv pip install google-generativeai"
            )

    def get_assessment(self, prompt: str) -> str:
        """Get assessment from Gemini API."""
        try:
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 1000,
                },
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")


class AnthropicProvider:
    """Anthropic Claude provider implementation."""

    def __init__(self, api_key: str = None, model: str = "claude-3-sonnet-20240229"):
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key. If None, reads from environment
            model: Model name to use (default: claude-3-sonnet-20240229)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided and ANTHROPIC_API_KEY environment variable not set"
            )

        # Import here to make it optional
        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: uv pip install anthropic"
            )

    def get_assessment(self, prompt: str) -> str:
        """Get assessment from Anthropic API."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")


def create_provider(provider_name: str, api_key: str = None) -> LLMProvider:
    """Factory function to create LLM providers.

    Args:
        provider_name: Name of the provider ("openai", "gemini", "anthropic")
        api_key: Optional API key. If not provided, reads from environment

    Returns:
        LLMProvider instance
    """
    providers = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "anthropic": AnthropicProvider,
    }

    if provider_name not in providers:
        raise ValueError(
            f"Unknown provider: {provider_name}. Available: {list(providers.keys())}"
        )

    return providers[provider_name](api_key=api_key)


def parse_llm_response(response: str) -> LLMAssessment:
    """Parse LLM response JSON into LLMAssessment model.

    Args:
        response: Raw JSON response from LLM

    Returns:
        Parsed LLMAssessment

    Raises:
        ValueError: If response cannot be parsed
    """
    try:
        # Clean up response (remove any markdown code blocks if present)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        # Parse JSON
        data = json.loads(response)
        return LLMAssessment(**data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to parse LLM response: {str(e)}")
