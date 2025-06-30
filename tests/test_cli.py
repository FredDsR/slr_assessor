"""Tests for the CLI module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner
from slr_assessor.cli import app


def test_cli_app_exists():
    """Test that the CLI app is properly configured."""
    assert app is not None
    assert app.info.name == "slr-assessor"

@patch('slr_assessor.cli.read_papers_from_csv')
@patch('slr_assessor.cli.create_provider')
@patch('slr_assessor.cli.UsageTracker')
@patch('slr_assessor.cli.write_evaluations_to_csv')
def test_screen_command_basic(mock_write_csv, mock_usage_tracker,
                                mock_create_provider, mock_read_papers):
    """Test basic screen command functionality."""
    # Mock the dependencies
    mock_papers = [Mock()]
    mock_papers[0].id = "paper_001"
    mock_papers[0].title = "Test Paper"
    mock_papers[0].abstract = "Test abstract"

    mock_read_papers.return_value = mock_papers

    mock_provider = Mock()
    mock_provider.get_assessment.return_value = ('{"assessments": [], "overall_summary": "test"}', Mock())
    mock_create_provider.return_value = mock_provider

    mock_tracker = Mock()
    mock_usage_tracker.return_value = mock_tracker

    runner = CliRunner()

    # This is a basic test structure - full CLI testing would require more setup
    # due to the complexity of mocking all dependencies
    with patch('slr_assessor.cli.console'):
        result = runner.invoke(app, [
            "screen",
            "test_input.csv",
            "--provider", "openai",
            "--output", "test_output.csv",
            "--api-key", "test-key"
        ])

        # The command should at least attempt to read papers
        mock_read_papers.assert_called_once()

def test_cli_help():
    """Test that CLI help works."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "slr-assessor" in result.output
    assert "paper screening" in result.output.lower()

def test_screen_command_help():
    """Test that screen command help works."""
    runner = CliRunner()
    result = runner.invoke(app, ["screen", "--help"])

    assert result.exit_code == 0
    assert "Screen papers using an LLM provider" in result.output

@patch('slr_assessor.cli.compare_evaluations')
@patch('slr_assessor.cli.read_evaluations_from_csv')
def test_compare_command_help(mock_read_evals, mock_compare):
    """Test that compare command help works."""
    runner = CliRunner()
    result = runner.invoke(app, ["compare", "--help"])

    assert result.exit_code == 0
    assert "Compare two evaluation results" in result.output

@patch('slr_assessor.cli.estimate_screening_cost')
@patch('slr_assessor.cli.read_papers_from_csv')
def test_estimate_command_help(mock_read_papers, mock_estimate):
    """Test that estimate command help works."""
    runner = CliRunner()
    result = runner.invoke(app, ["estimate-cost", "--help"])

    assert result.exit_code == 0
    assert "Estimate screening costs" in result.output


def test_screen_command_required_args():
    """Test that screen command requires necessary arguments."""
    runner = CliRunner()

    # Test missing required arguments
    result = runner.invoke(app, ["screen"])
    assert result.exit_code != 0

    # Test missing provider
    result = runner.invoke(app, ["screen", "input.csv"])
    assert result.exit_code != 0

    # Test missing output
    result = runner.invoke(app, ["screen", "input.csv", "--provider", "openai"])
    assert result.exit_code != 0

def test_compare_command_required_args():
    """Test that compare command requires necessary arguments."""
    runner = CliRunner()

    # Test missing required arguments
    result = runner.invoke(app, ["compare"])
    assert result.exit_code != 0

def test_estimate_command_required_args():
    """Test that estimate command requires necessary arguments."""
    runner = CliRunner()

    # Test missing required arguments
    result = runner.invoke(app, ["estimate"])
    assert result.exit_code != 0


# Note: Full CLI testing would require extensive mocking of file I/O,
# LLM providers, and other external dependencies. The tests above provide
# basic structure validation and help functionality testing.
# For complete CLI testing, consider using integration tests with
# temporary files and mock providers.
