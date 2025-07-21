"""Abstraction layer and concrete LLM provider integrations."""

import json
import os
from typing import Optional, Protocol, runtime_checkable

from ..models import LLMAssessment, TokenUsage
from ..utils.cost_calculator import calculate_cost


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers."""

    def get_assessment(self, prompt: str) -> tuple[str, TokenUsage]:
        """Get assessment from the LLM provider.

        Args:
            prompt: The formatted prompt to send to the LLM

        Returns:
            Tuple of (raw response string, token usage info)
        """
        ...


class OpenAIProvider:
    """OpenAI GPT provider implementation."""

    def __init__(self, model: str, api_key: Optional[str] = None):
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

    def get_assessment(self, prompt: str) -> tuple[str, TokenUsage]:
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

            # Extract token usage
            usage = response.usage
            token_usage = TokenUsage(
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                model=self.model,
                provider="openai",
            )

            # Calculate cost if pricing is available
            from ..utils.cost_calculator import calculate_cost

            try:
                cost = calculate_cost(
                    token_usage.input_tokens,
                    token_usage.output_tokens,
                    "openai",
                    self.model,
                )
                token_usage.estimated_cost = cost
            except:
                pass  # Cost calculation failed, keep None

            return response.choices[0].message.content, token_usage
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class GeminiProvider:
    """Google Gemini provider implementation."""

    def __init__(self, model: str, api_key: Optional[str] = None):
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
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "google-genai package not installed. Install with: uv pip install google-genai"
            )

    def get_assessment(self, prompt: str) -> tuple[str, TokenUsage]:
        """Get assessment from Gemini API."""
        try:
            from google.genai import types

            if "2.5" in self.model:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=1000,
                        thinking_config=types.ThinkingConfig(
                            thinking_budget=0
                        ),
                    ),
                )
            else:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=1000
                    ),
                )

            from ..utils.cost_calculator import calculate_cost

            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = response.usage_metadata.candidates_token_count
            if hasattr(response.usage_metadata, "thoughts_token_count") and response.usage_metadata.thoughts_token_count:
                output_tokens += response.usage_metadata.thoughts_token_count
            if hasattr(response.usage_metadata, "tool_use_prompt_token_count") and response.usage_metadata.tool_use_prompt_token_count:
                output_tokens += response.usage_metadata.tool_use_prompt_token_count

            token_usage = TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                model=self.model,
                provider="gemini",
            )

            # Calculate cost
            try:
                cost = calculate_cost(
                    token_usage.input_tokens,
                    token_usage.output_tokens,
                    "gemini",
                    self.model,
                )
                token_usage.estimated_cost = cost
            except Exception:
                pass  # Cost calculation failed, keep None

            return response.text, token_usage
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}") from e


class AnthropicProvider:
    """Anthropic Claude provider implementation."""

    def __init__(self, model: str, api_key: Optional[str] = None):
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

    def get_assessment(self, prompt: str) -> tuple[str, TokenUsage]:
        """Get assessment from Anthropic API."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract token usage from Anthropic response
            usage = response.usage
            token_usage = TokenUsage(
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                total_tokens=usage.input_tokens + usage.output_tokens,
                model=self.model,
                provider="anthropic",
            )

            # Calculate cost
            from ..utils.cost_calculator import calculate_cost

            try:
                cost = calculate_cost(
                    token_usage.input_tokens,
                    token_usage.output_tokens,
                    "anthropic",
                    self.model,
                )
                token_usage.estimated_cost = cost
            except Exception:
                pass  # Cost calculation failed, keep None

            return response.content[0].text, token_usage
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")


def create_provider(
    provider_name: str, api_key: Optional[str] = None, model: Optional[str] = None
) -> LLMProvider:
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

    default_model = {
        "openai": "gpt-4",
        "gemini": "gemini-2.5-flash",
        "anthropic": "claude-3-sonnet-20240229",
    }

    if provider_name not in providers:
        raise ValueError(
            f"Unknown provider: {provider_name}. Available: {list(providers.keys())}"
        )

    if model is None:
        model = default_model.get(provider_name, "gpt-4")

    return providers[provider_name](api_key=api_key, model=model)


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
