"""Tests for the usage tracker utility module."""

import json
import pytest
import tempfile
import os
from decimal import Decimal
from unittest.mock import Mock, patch
from slr_assessor.utils.usage_tracker import (
    UsageTracker,
    load_usage_report,
)
from slr_assessor.models import TokenUsage, UsageReport


class TestUsageTracker:
    """Test the UsageTracker class."""

    def test_init(self):
        """Test UsageTracker initialization."""
        tracker = UsageTracker("openai", "gpt-4")

        assert tracker.provider == "openai"
        assert tracker.model == "gpt-4"
        assert tracker.session_id is not None
        assert tracker.start_time is not None
        assert tracker.end_time is None
        assert tracker.total_papers_processed == 0
        assert tracker.successful_papers == 0
        assert tracker.failed_papers == 0
        assert len(tracker.paper_usages) == 0

    def test_add_usage(self, sample_token_usage):
        """Test adding token usage."""
        tracker = UsageTracker("openai", "gpt-4")

        tracker.add_usage(sample_token_usage)

        assert len(tracker.paper_usages) == 1
        assert tracker.paper_usages[0] == sample_token_usage
        assert tracker.total_papers_processed == 1
        assert tracker.successful_papers == 1
        assert tracker.failed_papers == 0

    def test_add_multiple_usages(self):
        """Test adding multiple token usages."""
        tracker = UsageTracker("openai", "gpt-4")

        usage1 = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            model="gpt-4",
            provider="openai",
            estimated_cost=Decimal("0.045"),
        )

        usage2 = TokenUsage(
            input_tokens=800,
            output_tokens=400,
            total_tokens=1200,
            model="gpt-4",
            provider="openai",
            estimated_cost=Decimal("0.036"),
        )

        tracker.add_usage(usage1)
        tracker.add_usage(usage2)

        assert len(tracker.paper_usages) == 2
        assert tracker.total_papers_processed == 2
        assert tracker.successful_papers == 2
        assert tracker.failed_papers == 0

    def test_add_failure(self):
        """Test recording failed paper processing."""
        tracker = UsageTracker("openai", "gpt-4")

        tracker.add_failure()

        assert tracker.total_papers_processed == 1
        assert tracker.successful_papers == 0
        assert tracker.failed_papers == 1
        assert len(tracker.paper_usages) == 0

    def test_mixed_success_and_failure(self, sample_token_usage):
        """Test tracking both successful and failed papers."""
        tracker = UsageTracker("openai", "gpt-4")

        tracker.add_usage(sample_token_usage)
        tracker.add_failure()
        tracker.add_usage(sample_token_usage)

        assert tracker.total_papers_processed == 3
        assert tracker.successful_papers == 2
        assert tracker.failed_papers == 1
        assert len(tracker.paper_usages) == 2

    def test_finish_session(self):
        """Test finishing a session."""
        tracker = UsageTracker("openai", "gpt-4")

        assert tracker.end_time is None

        tracker.finish_session()

        assert tracker.end_time is not None
        assert tracker.end_time != tracker.start_time

    def test_get_report_empty(self):
        """Test getting report with no usage data."""
        tracker = UsageTracker("openai", "gpt-4")

        report = tracker.get_report()

        assert isinstance(report, UsageReport)
        assert report.session_id == tracker.session_id
        assert report.provider == "openai"
        assert report.model == "gpt-4"
        assert report.total_papers_processed == 0
        assert report.successful_papers == 0
        assert report.failed_papers == 0
        assert report.total_input_tokens == 0
        assert report.total_output_tokens == 0
        assert report.total_tokens == 0
        assert report.total_cost == Decimal("0.00")
        assert report.average_tokens_per_paper == 0.0

    def test_get_report_with_usage(self):
        """Test getting report with usage data."""
        tracker = UsageTracker("openai", "gpt-4")

        usage1 = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            model="gpt-4",
            provider="openai",
            estimated_cost=Decimal("0.045"),
        )

        usage2 = TokenUsage(
            input_tokens=800,
            output_tokens=400,
            total_tokens=1200,
            model="gpt-4",
            provider="openai",
            estimated_cost=Decimal("0.036"),
        )

        tracker.add_usage(usage1)
        tracker.add_usage(usage2)
        tracker.add_failure()
        tracker.finish_session()

        report = tracker.get_report()

        assert report.total_papers_processed == 3
        assert report.successful_papers == 2
        assert report.failed_papers == 1
        assert report.total_input_tokens == 1800
        assert report.total_output_tokens == 900
        assert report.total_tokens == 2700
        assert report.total_cost == Decimal("0.081")
        assert report.average_tokens_per_paper == 1350.0
        assert report.end_time == tracker.end_time
        assert len(report.paper_usages) == 2

    def test_get_report_with_none_costs(self):
        """Test getting report when some usages have None estimated_cost."""
        tracker = UsageTracker("openai", "gpt-4")

        usage1 = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            model="gpt-4",
            provider="openai",
            estimated_cost=Decimal("0.045"),
        )

        usage2 = TokenUsage(
            input_tokens=800,
            output_tokens=400,
            total_tokens=1200,
            model="gpt-4",
            provider="openai",
            estimated_cost=None,  # No cost estimate
        )

        tracker.add_usage(usage1)
        tracker.add_usage(usage2)

        report = tracker.get_report()

        assert report.total_cost == Decimal("0.045")  # Only first usage counted
        assert report.total_tokens == 2700

    def test_save_report(self):
        """Test saving usage report to file."""
        tracker = UsageTracker("openai", "gpt-4")

        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            model="gpt-4",
            provider="openai",
            estimated_cost=Decimal("0.045"),
        )

        tracker.add_usage(usage)
        tracker.finish_session()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            tracker.save_report(temp_file_path)

            # Verify file was created and contains expected data
            assert os.path.exists(temp_file_path)

            with open(temp_file_path) as f:
                data = json.load(f)

            assert data["provider"] == "openai"
            assert data["model"] == "gpt-4"
            assert data["total_papers_processed"] == 1
            assert data["successful_papers"] == 1
            assert data["total_tokens"] == 1500
            assert float(data["total_cost"]) == 0.045
        finally:
            os.unlink(temp_file_path)

    def test_print_summary(self):
        """Test printing usage summary."""
        tracker = UsageTracker("openai", "gpt-4")

        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            model="gpt-4",
            provider="openai",
            estimated_cost=Decimal("0.045"),
        )

        tracker.add_usage(usage)
        tracker.add_failure()

        mock_console = Mock()
        tracker.print_summary(mock_console)

        # Verify that console.print was called multiple times
        assert mock_console.print.call_count > 5

        # Verify some of the expected content was printed
        calls = [call.args[0] for call in mock_console.print.call_args_list]
        summary_text = " ".join(str(call) for call in calls)

        assert "Usage Summary" in summary_text
        assert "openai/gpt-4" in summary_text
        assert "1/2" in summary_text  # 1 successful out of 2 total
        assert "Failed papers: 1" in summary_text
        assert "1,000" in summary_text  # Input tokens
        assert "500" in summary_text  # Output tokens
        assert "$0.0450" in summary_text  # Total cost

    def test_print_summary_no_cost(self):
        """Test printing summary when no cost information is available."""
        tracker = UsageTracker("openai", "gpt-4")

        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            model="gpt-4",
            provider="openai",
            estimated_cost=None,
        )

        tracker.add_usage(usage)

        mock_console = Mock()
        tracker.print_summary(mock_console)

        calls = [call.args[0] for call in mock_console.print.call_args_list]
        summary_text = " ".join(str(call) for call in calls)

        assert "Cost information not available" in summary_text

    def test_print_summary_no_failures(self):
        """Test printing summary when there are no failed papers."""
        tracker = UsageTracker("openai", "gpt-4")

        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            model="gpt-4",
            provider="openai",
            estimated_cost=Decimal("0.045"),
        )

        tracker.add_usage(usage)

        mock_console = Mock()
        tracker.print_summary(mock_console)

        calls = [call.args[0] for call in mock_console.print.call_args_list]
        summary_text = " ".join(str(call) for call in calls)

        # Should not mention failed papers when there are none
        assert "Failed papers" not in summary_text


class TestLoadUsageReport:
    """Test the load_usage_report function."""

    def test_load_usage_report_basic(self):
        """Test loading a basic usage report."""
        report_data = {
            "session_id": "test-session",
            "start_time": "2025-01-01T10:00:00",
            "end_time": "2025-01-01T11:00:00",
            "provider": "openai",
            "model": "gpt-4",
            "total_papers_processed": 10,
            "successful_papers": 9,
            "failed_papers": 1,
            "total_input_tokens": 10000,
            "total_output_tokens": 5000,
            "total_tokens": 15000,
            "total_cost": "0.45",
            "average_tokens_per_paper": 1500.0,
            "paper_usages": []
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(report_data, temp_file, indent=2)
            temp_file_path = temp_file.name

        try:
            report = load_usage_report(temp_file_path)

            assert isinstance(report, UsageReport)
            assert report.session_id == "test-session"
            assert report.provider == "openai"
            assert report.model == "gpt-4"
            assert report.total_papers_processed == 10
            assert report.total_cost == Decimal("0.45")
        finally:
            os.unlink(temp_file_path)

    def test_load_usage_report_with_paper_usages(self):
        """Test loading usage report with paper usages."""
        report_data = {
            "session_id": "test-session",
            "start_time": "2025-01-01T10:00:00",
            "provider": "openai",
            "model": "gpt-4",
            "total_papers_processed": 1,
            "successful_papers": 1,
            "failed_papers": 0,
            "total_input_tokens": 1000,
            "total_output_tokens": 500,
            "total_tokens": 1500,
            "total_cost": "0.045",
            "average_tokens_per_paper": 1500.0,
            "paper_usages": [
                {
                    "input_tokens": 1000,
                    "output_tokens": 500,
                    "total_tokens": 1500,
                    "model": "gpt-4",
                    "provider": "openai",
                    "estimated_cost": "0.045"
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(report_data, temp_file, indent=2)
            temp_file_path = temp_file.name

        try:
            report = load_usage_report(temp_file_path)

            assert len(report.paper_usages) == 1
            assert report.paper_usages[0].estimated_cost == Decimal("0.045")
            assert report.paper_usages[0].input_tokens == 1000
        finally:
            os.unlink(temp_file_path)

    def test_load_usage_report_no_costs(self):
        """Test loading usage report without cost information."""
        report_data = {
            "session_id": "test-session",
            "start_time": "2025-01-01T10:00:00",
            "provider": "openai",
            "model": "gpt-4",
            "total_papers_processed": 1,
            "successful_papers": 1,
            "failed_papers": 0,
            "total_input_tokens": 1000,
            "total_output_tokens": 500,
            "total_tokens": 1500,
            "average_tokens_per_paper": 1500.0,
            "paper_usages": [
                {
                    "input_tokens": 1000,
                    "output_tokens": 500,
                    "total_tokens": 1500,
                    "model": "gpt-4",
                    "provider": "openai"
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(report_data, temp_file, indent=2)
            temp_file_path = temp_file.name

        try:
            report = load_usage_report(temp_file_path)

            assert len(report.paper_usages) == 1
            assert report.paper_usages[0].estimated_cost is None
        finally:
            os.unlink(temp_file_path)

    def test_load_usage_report_file_not_found(self):
        """Test loading non-existent usage report file."""
        with pytest.raises(FileNotFoundError):
            load_usage_report("/nonexistent/file.json")

    def test_load_usage_report_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write("invalid json content")
            temp_file_path = temp_file.name

        try:
            with pytest.raises(json.JSONDecodeError):
                load_usage_report(temp_file_path)
        finally:
            os.unlink(temp_file_path)
