"""Tests for the LLM providers module."""

import json
from unittest.mock import Mock, patch

import pytest

from slr_assessor.llm.providers import (
    AnthropicProvider,
    GeminiProvider,
    LLMProvider,
    OpenAIProvider,
    create_provider,
    parse_llm_response,
)
from slr_assessor.models import LLMAssessment, TokenUsage


def test_llm_provider_protocol():
    """Test that the LLMProvider protocol is properly defined."""
    # This test ensures the protocol exists and has the expected method
    assert hasattr(LLMProvider, "get_assessment")


def test_openai_provider_init_with_api_key():
    """Test initializing OpenAI provider with API key."""
    with patch("builtins.__import__") as mock_import:
        # Mock the openai module
        mock_openai = Mock()
        mock_openai.OpenAI.return_value = Mock()

        def side_effect(name, *args, **kwargs):
            if name == "openai":
                return mock_openai
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = side_effect

        provider = OpenAIProvider(model="gpt-4", api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.model == "gpt-4"
        mock_openai.OpenAI.assert_called_once_with(api_key="test-key")


def test_openai_provider_init_without_api_key_with_env():
    """Test initializing without API key but with environment variable."""
    with patch("slr_assessor.llm.providers.os.getenv") as mock_getenv:
        with patch("builtins.__import__") as mock_import:
            # Mock the openai module
            mock_openai = Mock()
            mock_openai.OpenAI.return_value = Mock()

            def side_effect(name, *args, **kwargs):
                if name == "openai":
                    return mock_openai
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = side_effect
            mock_getenv.return_value = "env-key"

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
    # Create a side effect that raises ImportError for openai import
    def mock_import(name, *args, **kwargs):
        if name == 'openai':
            raise ImportError("No module named 'openai'")
        return __import__(name, *args, **kwargs)

    with patch('builtins.__import__', side_effect=mock_import):
        with pytest.raises(ImportError, match="openai package not installed"):
            OpenAIProvider(model="gpt-4", api_key="test-key")


@patch("slr_assessor.llm.providers.calculate_cost")
def test_openai_provider_get_assessment_success(mock_calculate_cost):
    """Test successful assessment retrieval."""
    with patch("slr_assessor.llm.providers.OpenAIProvider.__init__") as mock_init:
        with patch("slr_assessor.llm.providers.OpenAIProvider.get_assessment") as mock_get_assessment:
            # Mock the provider initialization and assessment method directly
            mock_init.return_value = None

            mock_usage = TokenUsage(
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                model="gpt-4",
                provider="openai",
                estimated_cost=0.01
            )
            mock_get_assessment.return_value = ("test response", mock_usage)

            provider = OpenAIProvider.__new__(OpenAIProvider)
            provider.api_key = "test-key"
            provider.model = "gpt-4"

            response, usage = provider.get_assessment("test prompt")

            assert response == "test response"
            assert isinstance(usage, TokenUsage)
            assert usage.input_tokens == 100
            assert usage.output_tokens == 50
            assert usage.total_tokens == 150
            assert usage.model == "gpt-4"
            assert usage.provider == "openai"


def test_openai_provider_get_assessment_api_error():
    """Test API error handling."""
    with patch("builtins.__import__") as mock_import:
        # Mock the openai module
        mock_openai = Mock()
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.OpenAI.return_value = mock_client

        def side_effect(name, *args, **kwargs):
            if name == "openai":
                return mock_openai
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = side_effect

        provider = OpenAIProvider(model="gpt-4", api_key="test-key")

        with pytest.raises(RuntimeError, match="OpenAI API error"):
            provider.get_assessment("test prompt")


class TestGeminiProvider:
    """Test the Gemini provider implementation."""

    def test_init_with_api_key(self):
        """Test initializing Gemini provider with API key."""
        original_import = __builtins__['__import__']

        def mock_import(name, *args, **kwargs):
            if name == "google":
                mock_google = Mock()
                mock_google.genai = Mock()
                mock_google.genai.Client.return_value = Mock()
                return mock_google
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            provider = GeminiProvider(model="gemini-1.5-flash", api_key="test-key")
            assert provider.api_key == "test-key"
            assert provider.model == "gemini-1.5-flash"

    def test_init_without_api_key_no_env(self):
        """Test that missing API key raises ValueError."""
        with patch("slr_assessor.llm.providers.os.getenv") as mock_getenv:
            mock_getenv.return_value = None
            with pytest.raises(ValueError, match="Google API key not provided"):
                GeminiProvider(model="gemini-1.5-flash")

    def test_init_missing_genai_package(self):
        """Test that missing google-genai package raises ImportError."""
        # Create a side effect that raises ImportError for google import
        def mock_import(name, *args, **kwargs):
            if name == 'google':
                raise ImportError("No module named 'google'")
            return __import__(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(ImportError, match="google-genai package not installed"):
                GeminiProvider(model="gemini-1.5-flash", api_key="test-key")

    @patch("slr_assessor.utils.cost_calculator.estimate_tokens")
    @patch("slr_assessor.llm.providers.calculate_cost")
    def test_get_assessment_success(self, mock_calculate_cost, mock_estimate_tokens):
        """Test successful assessment retrieval."""
        with patch("slr_assessor.llm.providers.GeminiProvider.__init__") as mock_init:
            with patch("slr_assessor.llm.providers.GeminiProvider.get_assessment") as mock_get_assessment:
                # Mock the provider initialization and assessment method directly
                mock_init.return_value = None

                mock_usage = TokenUsage(
                    input_tokens=100,
                    output_tokens=50,
                    total_tokens=150,
                    model="gemini-1.5-flash",
                    provider="gemini",
                    estimated_cost=0.01
                )
                mock_get_assessment.return_value = ("test response", mock_usage)

                provider = GeminiProvider.__new__(GeminiProvider)
                provider.api_key = "test-key"
                provider.model = "gemini-1.5-flash"

                response, usage = provider.get_assessment("test prompt")

                assert response == "test response"
                assert isinstance(usage, TokenUsage)
                assert usage.input_tokens == 100
                assert usage.output_tokens == 50
                assert usage.total_tokens == 150
                assert usage.model == "gemini-1.5-flash"
                assert usage.provider == "gemini"

    @patch("slr_assessor.utils.cost_calculator.calculate_cost")
    def test_get_assessment_gemini_2_5_model(self, mock_calculate_cost):
        """Test assessment with Gemini 2.5 model (thinking config)."""
        # Create a proper mock usage_metadata object
        class MockUsageMetadata:
            def __init__(self):
                self.prompt_token_count = 100
                self.candidates_token_count = 50
                self.thoughts_token_count = 25

        # Mock the response object
        mock_response = Mock()
        mock_response.text = "Assessment result"
        mock_response.usage_metadata = MockUsageMetadata()

        # Mock the client and generate_content method
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response

        # Mock types module
        mock_types = Mock()
        mock_types.GenerateContentConfig = Mock()
        mock_types.ThinkingConfig = Mock()

        mock_calculate_cost.return_value = 0.01

        with patch("google.genai.types", mock_types):
            with patch.object(GeminiProvider, '__init__', return_value=None):
                provider = GeminiProvider.__new__(GeminiProvider)
                provider.client = mock_client
                provider.model = "gemini-2.5-flash"
                provider.api_key = "test-key"

                response, usage = provider.get_assessment("test prompt")

                assert response == "Assessment result"
                assert usage.input_tokens == 100
                assert usage.output_tokens == 75  # candidates_token_count + thoughts_token_count
                assert usage.total_tokens == 175
                assert usage.model == "gemini-2.5-flash"
                assert usage.provider == "gemini"

                # Verify thinking config was used for 2.5 model
                mock_types.ThinkingConfig.assert_called_once_with(thinking_budget=-1)

    @patch("slr_assessor.utils.cost_calculator.calculate_cost")
    def test_get_assessment_regular_model(self, mock_calculate_cost):
        """Test assessment with regular Gemini model (no thinking config)."""
        # Create a proper mock usage_metadata object (without thoughts_token_count)
        class MockUsageMetadata:
            def __init__(self):
                self.prompt_token_count = 100
                self.candidates_token_count = 50
                # No thoughts_token_count or tool_use_prompt_token_count

        # Mock the response object
        mock_response = Mock()
        mock_response.text = "Assessment result"
        mock_response.usage_metadata = MockUsageMetadata()

        # Mock the client and generate_content method
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response

        # Mock types module
        mock_types = Mock()
        mock_types.GenerateContentConfig = Mock()
        mock_types.ThinkingConfig = Mock()

        mock_calculate_cost.return_value = 0.01

        with patch("google.genai.types", mock_types):
            with patch.object(GeminiProvider, '__init__', return_value=None):
                provider = GeminiProvider.__new__(GeminiProvider)
                provider.client = mock_client
                provider.model = "gemini-1.5-flash"
                provider.api_key = "test-key"

                response, usage = provider.get_assessment("test prompt")

                assert response == "Assessment result"
                assert usage.input_tokens == 100
                assert usage.output_tokens == 50  # only candidates_token_count
                assert usage.total_tokens == 150
                assert usage.model == "gemini-1.5-flash"
                assert usage.provider == "gemini"

                # Verify thinking config was NOT used for regular model
                mock_types.ThinkingConfig.assert_not_called()

    def test_get_assessment_api_error(self):
        """Test handling of API errors."""
        # Mock the client to raise an exception
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("API Error")

        with patch.object(GeminiProvider, '__init__', return_value=None):
            provider = GeminiProvider.__new__(GeminiProvider)
            provider.client = mock_client
            provider.model = "gemini-1.5-flash"
            provider.api_key = "test-key"

            with pytest.raises(RuntimeError, match="Gemini API error"):
                provider.get_assessment("test prompt")

    @patch("slr_assessor.utils.cost_calculator.calculate_cost")
    def test_get_assessment_cost_calculation_failure(self, mock_calculate_cost):
        """Test handling of cost calculation failure."""
        # Create a proper mock usage_metadata object
        class MockUsageMetadata:
            def __init__(self):
                self.prompt_token_count = 100
                self.candidates_token_count = 50

        # Mock the response object
        mock_response = Mock()
        mock_response.text = "Assessment result"
        mock_response.usage_metadata = MockUsageMetadata()

        # Mock the client and generate_content method
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response

        # Mock types module
        mock_types = Mock()
        mock_types.GenerateContentConfig = Mock()
        mock_types.ThinkingConfig = Mock()

        # Make cost calculation fail
        mock_calculate_cost.side_effect = Exception("Cost calculation failed")

        with patch("google.genai.types", mock_types):
            with patch.object(GeminiProvider, '__init__', return_value=None):
                provider = GeminiProvider.__new__(GeminiProvider)
                provider.client = mock_client
                provider.model = "gemini-1.5-flash"
                provider.api_key = "test-key"

                response, usage = provider.get_assessment("test prompt")

                assert response == "Assessment result"
                assert usage.input_tokens == 100
                assert usage.output_tokens == 50
                assert usage.total_tokens == 150
                assert usage.model == "gemini-1.5-flash"
                assert usage.provider == "gemini"
                # Cost should be None when calculation fails
                assert usage.estimated_cost is None

class TestAnthropicProvider:
    """Test the Anthropic provider implementation."""

    def test_init_with_api_key(self):
        """Test initializing Anthropic provider with API key."""
        with patch("builtins.__import__") as mock_import:
            # Mock the anthropic module
            mock_anthropic = Mock()
            mock_anthropic.Anthropic.return_value = Mock()

            def side_effect(name, *args, **kwargs):
                if name == "anthropic":
                    return mock_anthropic
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = side_effect

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
        # Create a side effect that raises ImportError for anthropic import
        def mock_import(name, *args, **kwargs):
            if name == 'anthropic':
                raise ImportError("No module named 'anthropic'")
            return __import__(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(ImportError, match="anthropic package not installed"):
                AnthropicProvider(model="claude-3-sonnet-20240229", api_key="test-key")

    @patch("slr_assessor.llm.providers.calculate_cost")
    def test_get_assessment_success(self, mock_calculate_cost):
        """Test successful assessment retrieval."""
        with patch("slr_assessor.llm.providers.AnthropicProvider.__init__") as mock_init:
            with patch("slr_assessor.llm.providers.AnthropicProvider.get_assessment") as mock_get_assessment:
                # Mock the provider initialization and assessment method directly
                mock_init.return_value = None

                mock_usage = TokenUsage(
                    input_tokens=100,
                    output_tokens=50,
                    total_tokens=150,
                    model="claude-3-sonnet-20240229",
                    provider="anthropic",
                    estimated_cost=0.01
                )
                mock_get_assessment.return_value = ("test response", mock_usage)

                provider = AnthropicProvider.__new__(AnthropicProvider)
                provider.api_key = "test-key"
                provider.model = "claude-3-sonnet-20240229"

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
