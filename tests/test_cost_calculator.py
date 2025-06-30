"""Tests for the cost calculator utility module."""

from decimal import Decimal
from unittest.mock import Mock, patch

from slr_assessor.models import CostEstimate
from slr_assessor.utils.cost_calculator import (
    PRICING_TABLE,
    calculate_cost,
    estimate_screening_cost,
    estimate_tokens,
    get_pricing_info,
    get_provider_models,
)


def test_pricing_table_structure():
    """Test that pricing table has expected structure."""
    assert isinstance(PRICING_TABLE, dict)
    assert "openai" in PRICING_TABLE
    assert "gemini" in PRICING_TABLE
    assert "anthropic" in PRICING_TABLE

def test_pricing_table_models():
    """Test that expected models are in pricing table."""
    openai_models = PRICING_TABLE["openai"]
    assert "gpt-4" in openai_models
    assert "gpt-3.5-turbo" in openai_models

    gemini_models = PRICING_TABLE["gemini"]
    assert "gemini-2.5-flash" in gemini_models
    assert "gemini-1.5-flash" in gemini_models

    anthropic_models = PRICING_TABLE["anthropic"]
    assert "claude-3-sonnet-20240229" in anthropic_models

def test_pricing_table_values():
    """Test that pricing values are valid Decimals."""
    for provider, models in PRICING_TABLE.items():
        for model, pricing in models.items():
            assert "input" in pricing
            assert "output" in pricing
            assert isinstance(pricing["input"], Decimal)
            assert isinstance(pricing["output"], Decimal)
            assert pricing["input"] >= 0
            assert pricing["output"] >= 0


@patch("slr_assessor.utils.cost_calculator.tiktoken")
def test_estimate_tokens_gpt_model(mock_tiktoken):
    """Test token estimation for GPT models."""
    mock_encoding = Mock()
    mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
    mock_tiktoken.encoding_for_model.return_value = mock_encoding

    token_count = estimate_tokens("test text", "gpt-4")

    assert token_count == 5
    mock_tiktoken.encoding_for_model.assert_called_once_with("gpt-4")
    mock_encoding.encode.assert_called_once_with("test text")

def test_estimate_tokens_non_gpt_model():
    """Test token estimation for non-GPT models."""
    text = "This is a test text"  # 19 characters
    token_count = estimate_tokens(text, "gemini-1.5-flash")

    # Should use character-based estimation (19 // 4 = 4)
    assert token_count == 4

@patch("slr_assessor.utils.cost_calculator.tiktoken")
def test_estimate_tokens_tiktoken_error(mock_tiktoken):
    """Test fallback when tiktoken fails."""
    mock_tiktoken.encoding_for_model.side_effect = Exception("tiktoken error")

    text = "This is a test text"  # 19 characters
    token_count = estimate_tokens(text, "gpt-4")

    # Should fall back to character-based estimation
    assert token_count == 4

def test_estimate_tokens_empty_text():
    """Test token estimation for empty text."""
    token_count = estimate_tokens("", "gpt-4")
    assert token_count == 0

def test_estimate_tokens_long_text():
    """Test token estimation for long text."""
    text = "word " * 1000  # 5000 characters
    token_count = estimate_tokens(text, "gemini-1.5-flash")

    # Should use character-based estimation (5000 // 4 = 1250)
    assert token_count == 1250


def test_calculate_cost_known_model():
    """Test cost calculation for known model."""
    cost = calculate_cost(1000, 500, "openai", "gpt-4")

    # GPT-4: input $0.030/1K, output $0.060/1K
    # (1000/1000 * 0.030) + (500/1000 * 0.060) = 0.030 + 0.030 = 0.060
    expected_cost = Decimal("0.060")
    assert cost == expected_cost

def test_calculate_cost_unknown_provider():
    """Test cost calculation for unknown provider."""
    cost = calculate_cost(1000, 500, "unknown", "unknown-model")
    assert cost == Decimal("0.00")

def test_calculate_cost_unknown_model():
    """Test cost calculation for unknown model."""
    cost = calculate_cost(1000, 500, "openai", "unknown-model")
    assert cost == Decimal("0.00")

def test_calculate_cost_zero_tokens():
    """Test cost calculation with zero tokens."""
    cost = calculate_cost(0, 0, "openai", "gpt-4")
    assert cost == Decimal("0.00")

def test_calculate_cost_gemini_model():
    """Test cost calculation for Gemini model."""
    cost = calculate_cost(1000, 500, "gemini", "gemini-2.5-flash")

    # Gemini 2.5 Flash: input $0.000075/1K, output $0.0003/1K
    expected_cost = Decimal("0.000075") + Decimal("0.00015")
    assert cost == expected_cost

def test_calculate_cost_anthropic_model():
    """Test cost calculation for Anthropic model."""
    cost = calculate_cost(1000, 500, "anthropic", "claude-3-sonnet-20240229")

    # Claude 3 Sonnet: input $0.003/1K, output $0.015/1K
    expected_cost = Decimal("0.003") + Decimal("0.0075")
    assert cost == expected_cost


@patch("slr_assessor.llm.prompt.format_assessment_prompt")
@patch("slr_assessor.utils.cost_calculator.estimate_tokens")
def test_estimate_screening_cost_basic(mock_estimate_tokens, mock_format_prompt):
    """Test basic screening cost estimation."""
    mock_format_prompt.return_value = "formatted prompt"
    mock_estimate_tokens.return_value = 800  # input tokens

    estimate = estimate_screening_cost(
        num_papers=10,
        sample_abstract="test abstract",
        provider="openai",
        model="gpt-4"
    )

    assert isinstance(estimate, CostEstimate)
    assert estimate.total_papers == 10
    assert estimate.estimated_input_tokens_per_paper == 800
    assert estimate.estimated_output_tokens_per_paper == 500
    assert estimate.estimated_total_tokens == 13000  # (800 + 500) * 10
    assert estimate.provider == "openai"
    assert estimate.model == "gpt-4"

    # Cost calculation: (8000/1000 * 0.030) + (5000/1000 * 0.060) = 0.24 + 0.30 = 0.54
    assert estimate.estimated_total_cost == Decimal("0.54")

@patch("slr_assessor.llm.prompt.format_assessment_prompt")
@patch("slr_assessor.utils.cost_calculator.estimate_tokens")
def test_estimate_screening_cost_unknown_model(mock_estimate_tokens, mock_format_prompt):
    """Test screening cost estimation for unknown model."""
    mock_format_prompt.return_value = "formatted prompt"
    mock_estimate_tokens.return_value = 800

    estimate = estimate_screening_cost(
        num_papers=5,
        sample_abstract="test abstract",
        provider="unknown",
        model="unknown-model"
    )

    assert estimate.estimated_total_cost == Decimal("0.00")
    assert estimate.cost_per_input_token == Decimal("0.00")
    assert estimate.cost_per_output_token == Decimal("0.00")

@patch("slr_assessor.llm.prompt.format_assessment_prompt")
@patch("slr_assessor.utils.cost_calculator.estimate_tokens")
def test_estimate_screening_cost_zero_papers(mock_estimate_tokens, mock_format_prompt):
    """Test screening cost estimation for zero papers."""
    mock_format_prompt.return_value = "formatted prompt"
    mock_estimate_tokens.return_value = 800

    estimate = estimate_screening_cost(
        num_papers=0,
        sample_abstract="test abstract",
        provider="openai",
        model="gpt-4"
    )

    assert estimate.total_papers == 0
    assert estimate.estimated_total_tokens == 0
    assert estimate.estimated_total_cost == Decimal("0.00")

@patch("slr_assessor.llm.prompt.format_assessment_prompt")
@patch("slr_assessor.utils.cost_calculator.estimate_tokens")
def test_estimate_screening_cost_large_batch(mock_estimate_tokens, mock_format_prompt):
    """Test screening cost estimation for large batch."""
    mock_format_prompt.return_value = "formatted prompt"
    mock_estimate_tokens.return_value = 1000

    estimate = estimate_screening_cost(
        num_papers=1000,
        sample_abstract="test abstract",
        provider="gemini",
        model="gemini-2.5-flash"
    )

    assert estimate.total_papers == 1000
    assert estimate.estimated_total_tokens == 1500000  # (1000 + 500) * 1000

    # Gemini 2.5 Flash pricing
    expected_cost = (Decimal("1000000") / 1000 * Decimal("0.000075")) + \
                    (Decimal("500000") / 1000 * Decimal("0.0003"))
    assert estimate.estimated_total_cost == expected_cost


def test_get_openai_models():
    """Test getting OpenAI models."""
    models = get_provider_models("openai")
    assert isinstance(models, list)
    assert "gpt-4" in models
    assert "gpt-3.5-turbo" in models

def test_get_gemini_models():
    """Test getting Gemini models."""
    models = get_provider_models("gemini")
    assert isinstance(models, list)
    assert "gemini-2.5-flash" in models
    assert "gemini-1.5-flash" in models

def test_get_anthropic_models():
    """Test getting Anthropic models."""
    models = get_provider_models("anthropic")
    assert isinstance(models, list)
    assert "claude-3-sonnet-20240229" in models

def test_get_unknown_provider_models():
    """Test getting models for unknown provider."""
    models = get_provider_models("unknown")
    assert models == []


def test_get_pricing_info_known_model():
    """Test getting pricing info for known model."""
    pricing = get_pricing_info("openai", "gpt-4")

    assert isinstance(pricing, dict)
    assert "input" in pricing
    assert "output" in pricing
    assert pricing["input"] == Decimal("0.030")
    assert pricing["output"] == Decimal("0.060")

def test_get_pricing_info_unknown_provider():
    """Test getting pricing info for unknown provider."""
    pricing = get_pricing_info("unknown", "unknown-model")

    assert pricing["input"] == Decimal("0.00")
    assert pricing["output"] == Decimal("0.00")

def test_get_pricing_info_unknown_model():
    """Test getting pricing info for unknown model."""
    pricing = get_pricing_info("openai", "unknown-model")

    assert pricing["input"] == Decimal("0.00")
    assert pricing["output"] == Decimal("0.00")

def test_get_pricing_info_gemini():
    """Test getting pricing info for Gemini model."""
    pricing = get_pricing_info("gemini", "gemini-2.5-flash")

    assert pricing["input"] == Decimal("0.000075")
    assert pricing["output"] == Decimal("0.0003")

def test_get_pricing_info_anthropic():
    """Test getting pricing info for Anthropic model."""
    pricing = get_pricing_info("anthropic", "claude-3-sonnet-20240229")

    assert pricing["input"] == Decimal("0.003")
    assert pricing["output"] == Decimal("0.015")
