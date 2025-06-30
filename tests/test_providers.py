"""Tests for the LLM providers module."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from slr_assessor.llm.providers import (
    LLMProvider,
    OpenAIProvider,
    GeminiProvider,
    AnthropicProvider,
    create_provider,
    parse_llm_response,
)
from slr_assessor.models import LLMAssessment, QAResponseItem, TokenUsage


def test_llm_provider_protocol():
    """Test that the LLMProvider protocol is properly defined."""
    # This test ensures the protocol exists and has the expected method
    assert hasattr(LLMProvider, "get_assessment")


def test_openai_provider_init_with_api_key():
    """Test initializing OpenAI provider with API key."""
    with patch("slr_assessor.llm.providers.openai") as mock_openai:
        mock_openai.OpenAI.return_value = Mock()
        provider = OpenAIProvider(model="gpt-4", api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.model == "gpt-4"
        mock_openai.OpenAI.assert_called_once_with(api_key="test-key")


def test_openai_provider_init_without_api_key_with_env():
    """Test initializing without API key but with environment variable."""
    with patch("slr_assessor.llm.providers.os.getenv") as mock_getenv:
        with patch("slr_assessor.llm.providers.openai") as mock_openai:
            mock_getenv.return_value = "env-key"
            mock_openai.OpenAI.return_value = Mock()
            provider = OpenAIProvider(model="gpt-4")
            assert provider.api_key == "env-key"


def test_openai_provider_init_without_api_key_no_env():
    """Test that missing API key raises ValueError."""
    with patch("slr_assessor.llm.providers.os.getenv") as mock_getenv:
        mock_getenv.return_value = None
        with pytest.raises(ValueError, match="OpenAI API key not provided"):
            OpenAIProvider(model="gpt-4")


def test_openai_provider_init_missing_package():
    """Test that missing openai package raises ImportError."""
    with patch("slr_assessor.llm.providers.openai", side_effect=ImportError):
        with pytest.raises(ImportError, match="openai package not installed"):
            OpenAIProvider(model="gpt-4", api_key="test-key")


@patch("slr_assessor.llm.providers.openai")
@patch("slr_assessor.llm.providers.calculate_cost")
def test_openai_provider_get_assessment_success(mock_calculate_cost, mock_openai):
    """Test successful assessment retrieval."""
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "test response"
    mock_response.usage.prompt_tokens = 100
    mock_response.usage.completion_tokens = 50
    mock_response.usage.total_tokens = 150

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.OpenAI.return_value = mock_client
    mock_calculate_cost.return_value = 0.01

    provider = OpenAIProvider(model="gpt-4", api_key="test-key")
    response, usage = provider.get_assessment("test prompt")

    assert response == "test response"
    assert isinstance(usage, TokenUsage)
    assert usage.input_tokens == 100
    assert usage.output_tokens == 50
    assert usage.total_tokens == 150
    assert usage.model == "gpt-4"
    assert usage.provider == "openai"


@patch("slr_assessor.llm.providers.openai")
def test_openai_provider_get_assessment_api_error(mock_openai):
    """Test API error handling."""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.OpenAI.return_value = mock_client

    provider = OpenAIProvider(model="gpt-4", api_key="test-key")

    with pytest.raises(RuntimeError, match="OpenAI API error"):
        provider.get_assessment("test prompt")


class TestGeminiProvider:
    """Test the Gemini provider implementation."""

    def test_init_with_api_key(self):
        """Test initializing Gemini provider with API key."""
        with patch("slr_assessor.llm.providers.google.generativeai") as mock_genai:
            mock_genai.GenerativeModel.return_value = Mock()
            provider = GeminiProvider(model="gemini-1.5-flash", api_key="test-key")
            assert provider.api_key == "test-key"
            assert provider.model == "gemini-1.5-flash"
            mock_genai.configure.assert_called_once_with(api_key="test-key")

    def test_init_without_api_key_no_env(self):
        """Test that missing API key raises ValueError."""
        with patch("slr_assessor.llm.providers.os.getenv") as mock_getenv:
            mock_getenv.return_value = None
            with pytest.raises(ValueError, match="Google API key not provided"):
                GeminiProvider(model="gemini-1.5-flash")

    def test_init_missing_genai_package(self):
        """Test that missing google-generativeai package raises ImportError."""
        with patch("slr_assessor.llm.providers.google.generativeai", side_effect=ImportError):
            with pytest.raises(ImportError, match="google-generativeai package not installed"):
                GeminiProvider(model="gemini-1.5-flash", api_key="test-key")

    @patch("slr_assessor.llm.providers.google.generativeai")
    @patch("slr_assessor.llm.providers.estimate_tokens")
    @patch("slr_assessor.llm.providers.calculate_cost")
    def test_get_assessment_success(self, mock_calculate_cost, mock_estimate_tokens, mock_genai):
        """Test successful assessment retrieval."""
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = "test response"

        mock_client = Mock()
        mock_client.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_client
        mock_estimate_tokens.side_effect = [100, 50]  # input, output tokens
        mock_calculate_cost.return_value = 0.01

        provider = GeminiProvider(model="gemini-1.5-flash", api_key="test-key")
        response, usage = provider.get_assessment("test prompt")

        assert response == "test response"
        assert isinstance(usage, TokenUsage)
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 150
        assert usage.model == "gemini-1.5-flash"
        assert usage.provider == "gemini"


class TestAnthropicProvider:
    """Test the Anthropic provider implementation."""

    def test_init_with_api_key(self):
        """Test initializing Anthropic provider with API key."""
        with patch("slr_assessor.llm.providers.anthropic") as mock_anthropic:
            mock_anthropic.Anthropic.return_value = Mock()
            provider = AnthropicProvider(model="claude-3-sonnet-20240229", api_key="test-key")
            assert provider.api_key == "test-key"
            assert provider.model == "claude-3-sonnet-20240229"
            mock_anthropic.Anthropic.assert_called_once_with(api_key="test-key")

    def test_init_without_api_key_no_env(self):
        """Test that missing API key raises ValueError."""
        with patch("slr_assessor.llm.providers.os.getenv") as mock_getenv:
            mock_getenv.return_value = None
            with pytest.raises(ValueError, match="Anthropic API key not provided"):
                AnthropicProvider(model="claude-3-sonnet-20240229")

    def test_init_missing_anthropic_package(self):
        """Test that missing anthropic package raises ImportError."""
        with patch("slr_assessor.llm.providers.anthropic", side_effect=ImportError):
            with pytest.raises(ImportError, match="anthropic package not installed"):
                AnthropicProvider(model="claude-3-sonnet-20240229", api_key="test-key")

    @patch("slr_assessor.llm.providers.anthropic")
    @patch("slr_assessor.llm.providers.calculate_cost")
    def test_get_assessment_success(self, mock_calculate_cost, mock_anthropic):
        """Test successful assessment retrieval."""
        # Mock Anthropic response
        mock_usage = Mock()
        mock_usage.input_tokens = 100
        mock_usage.output_tokens = 50

        mock_content = Mock()
        mock_content.text = "test response"

        mock_response = Mock()
        mock_response.usage = mock_usage
        mock_response.content = [mock_content]

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client
        mock_calculate_cost.return_value = 0.01

        provider = AnthropicProvider(model="claude-3-sonnet-20240229", api_key="test-key")
        response, usage = provider.get_assessment("test prompt")

        assert response == "test response"
        assert isinstance(usage, TokenUsage)
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 150
        assert usage.model == "claude-3-sonnet-20240229"
        assert usage.provider == "anthropic"


class TestCreateProvider:
    """Test the create_provider factory function."""

    @patch("slr_assessor.llm.providers.OpenAIProvider")
    def test_create_openai_provider(self, mock_openai_provider):
        """Test creating OpenAI provider."""
        mock_instance = Mock()
        mock_openai_provider.return_value = mock_instance

        provider = create_provider("openai", api_key="test-key", model="gpt-4")

        mock_openai_provider.assert_called_once_with(api_key="test-key", model="gpt-4")
        assert provider == mock_instance

    @patch("slr_assessor.llm.providers.GeminiProvider")
    def test_create_gemini_provider(self, mock_gemini_provider):
        """Test creating Gemini provider."""
        mock_instance = Mock()
        mock_gemini_provider.return_value = mock_instance

        provider = create_provider("gemini", api_key="test-key", model="gemini-1.5-flash")

        mock_gemini_provider.assert_called_once_with(api_key="test-key", model="gemini-1.5-flash")
        assert provider == mock_instance

    @patch("slr_assessor.llm.providers.AnthropicProvider")
    def test_create_anthropic_provider(self, mock_anthropic_provider):
        """Test creating Anthropic provider."""
        mock_instance = Mock()
        mock_anthropic_provider.return_value = mock_instance

        provider = create_provider("anthropic", api_key="test-key", model="claude-3-sonnet-20240229")

        mock_anthropic_provider.assert_called_once_with(api_key="test-key", model="claude-3-sonnet-20240229")
        assert provider == mock_instance

    def test_create_unknown_provider(self):
        """Test creating unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider: unknown"):
            create_provider("unknown")

    @patch("slr_assessor.llm.providers.OpenAIProvider")
    def test_create_provider_default_model(self, mock_openai_provider):
        """Test creating provider with default model."""
        mock_instance = Mock()
        mock_openai_provider.return_value = mock_instance

        provider = create_provider("openai", api_key="test-key")

        mock_openai_provider.assert_called_once_with(api_key="test-key", model="gpt-4")

    @patch("slr_assessor.llm.providers.GeminiProvider")
    def test_create_provider_default_gemini_model(self, mock_gemini_provider):
        """Test creating Gemini provider with default model."""
        mock_instance = Mock()
        mock_gemini_provider.return_value = mock_instance

        provider = create_provider("gemini", api_key="test-key")

        mock_gemini_provider.assert_called_once_with(api_key="test-key", model="gemini-2.5-flash")


class TestParseLLMResponse:
    """Test the parse_llm_response function."""

    def test_parse_valid_json_response(self):
        """Test parsing valid JSON response."""
        response_data = {
            "assessments": [
                {
                    "qa_id": "QA1",
                    "question": "Test question?",
                    "score": 1.0,
                    "reason": "Test reason"
                }
            ],
            "overall_summary": "Test summary"
        }
        response_json = json.dumps(response_data)

        assessment = parse_llm_response(response_json)

        assert isinstance(assessment, LLMAssessment)
        assert len(assessment.assessments) == 1
        assert assessment.assessments[0].qa_id == "QA1"
        assert assessment.assessments[0].score == 1.0
        assert assessment.overall_summary == "Test summary"

    def test_parse_json_with_markdown_blocks(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        response_data = {
            "assessments": [],
            "overall_summary": "Test summary"
        }
        response_json = f"```json\n{json.dumps(response_data)}\n```"

        assessment = parse_llm_response(response_json)

        assert isinstance(assessment, LLMAssessment)
        assert assessment.overall_summary == "Test summary"

    def test_parse_json_with_code_blocks(self):
        """Test parsing JSON wrapped in generic code blocks."""
        response_data = {
            "assessments": [],
            "overall_summary": "Test summary"
        }
        response_json = f"```\n{json.dumps(response_data)}\n```"

        assessment = parse_llm_response(response_json)

        assert isinstance(assessment, LLMAssessment)
        assert assessment.overall_summary == "Test summary"

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises ValueError."""
        invalid_json = '{"assessments": [}, "invalid": json}'

        with pytest.raises(ValueError, match="Invalid JSON response from LLM"):
            parse_llm_response(invalid_json)

    def test_parse_missing_required_fields(self):
        """Test parsing JSON missing required fields."""
        incomplete_data = {"assessments": []}  # Missing overall_summary
        response_json = json.dumps(incomplete_data)

        with pytest.raises(ValueError, match="Failed to parse LLM response"):
            parse_llm_response(response_json)

    def test_parse_empty_response(self):
        """Test parsing empty response."""
        with pytest.raises(ValueError, match="Invalid JSON response from LLM"):
            parse_llm_response("")

    def test_parse_whitespace_response(self):
        """Test parsing response with only whitespace."""
        with pytest.raises(ValueError, match="Invalid JSON response from LLM"):
            parse_llm_response("   \n\t   ")

    def test_parse_complex_valid_response(self, sample_llm_assessment):
        """Test parsing complex valid response."""
        response_data = {
            "assessments": [
                {
                    "qa_id": "QA1",
                    "question": "Is this paper relevant?",
                    "score": 1.0,
                    "reason": "Highly relevant to the research question."
                },
                {
                    "qa_id": "QA2",
                    "question": "Is the methodology sound?",
                    "score": 0.5,
                    "reason": "Methodology has some limitations."
                }
            ],
            "overall_summary": "Paper is relevant but has methodological concerns."
        }
        response_json = json.dumps(response_data, indent=2)

        assessment = parse_llm_response(response_json)

        assert isinstance(assessment, LLMAssessment)
        assert len(assessment.assessments) == 2
        assert assessment.assessments[0].score == 1.0
        assert assessment.assessments[1].score == 0.5
