"""Cost calculation and token usage utilities for LLM providers."""

from decimal import Decimal
from typing import Dict, Tuple
from ..models import TokenUsage, CostEstimate
import tiktoken


# Pricing information per provider and model (USD per 1K tokens)
# Prices as of June 2025 - should be updated regularly
PRICING_TABLE = {
    "openai": {
        "gpt-4": {"input": Decimal("0.030"), "output": Decimal("0.060")},
        "gpt-4-turbo": {"input": Decimal("0.010"), "output": Decimal("0.030")},
        "gpt-3.5-turbo": {"input": Decimal("0.0015"), "output": Decimal("0.002")},
    },
    "gemini": {
        "gemini-2.5-flash": {"input": Decimal("0.000075"), "output": Decimal("0.0003")},
        "gemini-2.5-pro": {"input": Decimal("0.00075"), "output": Decimal("0.003")},
        "gemini-1.5-flash": {"input": Decimal("0.000075"), "output": Decimal("0.0003")},
        "gemini-1.5-pro": {"input": Decimal("0.00075"), "output": Decimal("0.003")},
    },
    "anthropic": {
        "claude-3-sonnet-20240229": {
            "input": Decimal("0.003"),
            "output": Decimal("0.015"),
        },
        "claude-3-haiku-20240307": {
            "input": Decimal("0.00025"),
            "output": Decimal("0.00125"),
        },
        "claude-3-opus-20240229": {
            "input": Decimal("0.015"),
            "output": Decimal("0.075"),
        },
        "claude-3-5-sonnet-20241022": {
            "input": Decimal("0.003"),
            "output": Decimal("0.015"),
        },
    },
}


def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    """Estimate token count for a given text.

    Args:
        text: Text to estimate tokens for
        model: Model name for tokenizer selection

    Returns:
        Estimated token count
    """
    try:
        # Use tiktoken for OpenAI models
        if model.startswith("gpt"):
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        else:
            # Rough estimation for non-OpenAI models (4 chars per token average)
            return len(text) // 4
    except Exception:
        # Fallback to character-based estimation
        return len(text) // 4


def calculate_cost(
    input_tokens: int, output_tokens: int, provider: str, model: str
) -> Decimal:
    """Calculate cost for token usage.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        provider: Provider name
        model: Model name

    Returns:
        Total cost in USD
    """
    if provider not in PRICING_TABLE or model not in PRICING_TABLE[provider]:
        return Decimal("0.00")  # Unknown pricing

    pricing = PRICING_TABLE[provider][model]
    input_cost = (Decimal(input_tokens) / 1000) * pricing["input"]
    output_cost = (Decimal(output_tokens) / 1000) * pricing["output"]

    return input_cost + output_cost


def estimate_screening_cost(
    num_papers: int, sample_abstract: str, provider: str, model: str
) -> CostEstimate:
    """Estimate total cost for screening a batch of papers.

    Args:
        num_papers: Number of papers to screen
        sample_abstract: Sample abstract for token estimation
        provider: LLM provider name
        model: Model name

    Returns:
        CostEstimate object with breakdown
    """
    from ..llm.prompt import format_assessment_prompt

    # Estimate tokens for a typical request
    full_prompt = format_assessment_prompt(sample_abstract)
    estimated_input_tokens = estimate_tokens(full_prompt, model)

    # Estimate output tokens (typical response is ~400-600 tokens)
    estimated_output_tokens = 500

    # Get pricing
    if provider in PRICING_TABLE and model in PRICING_TABLE[provider]:
        pricing = PRICING_TABLE[provider][model]
        cost_per_input = pricing["input"]
        cost_per_output = pricing["output"]
    else:
        cost_per_input = Decimal("0.00")
        cost_per_output = Decimal("0.00")

    # Calculate totals
    total_input_tokens = estimated_input_tokens * num_papers
    total_output_tokens = estimated_output_tokens * num_papers
    total_tokens = total_input_tokens + total_output_tokens

    input_cost = (Decimal(total_input_tokens) / 1000) * cost_per_input
    output_cost = (Decimal(total_output_tokens) / 1000) * cost_per_output
    total_cost = input_cost + output_cost

    return CostEstimate(
        total_papers=num_papers,
        estimated_input_tokens_per_paper=estimated_input_tokens,
        estimated_output_tokens_per_paper=estimated_output_tokens,
        estimated_total_tokens=total_tokens,
        estimated_total_cost=total_cost,
        cost_per_input_token=cost_per_input,
        cost_per_output_token=cost_per_output,
        provider=provider,
        model=model,
    )


def get_provider_models(provider: str) -> list:
    """Get available models for a provider.

    Args:
        provider: Provider name

    Returns:
        List of available model names
    """
    return list(PRICING_TABLE.get(provider, {}).keys())


def get_pricing_info(provider: str, model: str) -> Dict[str, Decimal]:
    """Get pricing information for a specific model.

    Args:
        provider: Provider name
        model: Model name

    Returns:
        Dictionary with input and output pricing per 1K tokens
    """
    return PRICING_TABLE.get(provider, {}).get(
        model, {"input": Decimal("0.00"), "output": Decimal("0.00")}
    )
