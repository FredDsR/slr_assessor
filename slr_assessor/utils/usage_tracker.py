"""Usage tracking and reporting utilities."""

import json
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..models import TokenUsage, UsageReport


class UsageTracker:
    """Tracks token usage and costs during a screening session."""

    def __init__(self, provider: str, model: str):
        """Initialize usage tracker.

        Args:
            provider: LLM provider name
            model: Model name
        """
        self.session_id = str(uuid.uuid4())
        self.provider = provider
        self.model = model
        self.start_time = datetime.now().isoformat()
        self.end_time: Optional[str] = None

        self.total_papers_processed = 0
        self.successful_papers = 0
        self.failed_papers = 0
        self.paper_usages: list[TokenUsage] = []

    def add_usage(self, token_usage: TokenUsage) -> None:
        """Add token usage for a processed paper.

        Args:
            token_usage: Token usage information
        """
        self.paper_usages.append(token_usage)
        self.total_papers_processed += 1
        self.successful_papers += 1

    def add_failure(self) -> None:
        """Record a failed paper processing."""
        self.total_papers_processed += 1
        self.failed_papers += 1

    def finish_session(self) -> None:
        """Mark the session as completed."""
        self.end_time = datetime.now().isoformat()

    def get_report(self) -> UsageReport:
        """Generate usage report for the session.

        Returns:
            UsageReport with session statistics
        """
        total_input_tokens = sum(usage.input_tokens for usage in self.paper_usages)
        total_output_tokens = sum(usage.output_tokens for usage in self.paper_usages)
        total_tokens = total_input_tokens + total_output_tokens
        total_cost = sum(
            usage.estimated_cost or Decimal("0.00") for usage in self.paper_usages
        )

        average_tokens = total_tokens / max(self.successful_papers, 1)

        return UsageReport(
            session_id=self.session_id,
            start_time=self.start_time,
            end_time=self.end_time,
            provider=self.provider,
            model=self.model,
            total_papers_processed=self.total_papers_processed,
            successful_papers=self.successful_papers,
            failed_papers=self.failed_papers,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_tokens=total_tokens,
            total_cost=total_cost,
            average_tokens_per_paper=average_tokens,
            paper_usages=self.paper_usages,
        )

    def save_report(self, filepath: str) -> None:
        """Save usage report to JSON file.

        Args:
            filepath: Path to save the report
        """
        report = self.get_report()

        # Convert the report to dict and handle Decimal serialization
        report_data = report.model_dump()

        # Convert Decimal values to strings for JSON serialization
        def convert_decimals(obj):
            if isinstance(obj, Decimal):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            return obj

        serializable_data = convert_decimals(report_data)

        with open(filepath, "w") as f:
            json.dump(serializable_data, f, indent=2)

    def print_summary(self, console) -> None:
        """Print usage summary to console.

        Args:
            console: Rich console instance
        """
        report = self.get_report()

        console.print("\n[bold cyan]📊 Usage Summary[/bold cyan]")
        console.print(f"Session ID: {report.session_id}")
        console.print(f"Provider/Model: {report.provider}/{report.model}")
        console.print(
            f"Papers processed: {report.successful_papers}/{report.total_papers_processed}"
        )

        if report.failed_papers > 0:
            console.print(f"[yellow]Failed papers: {report.failed_papers}[/yellow]")

        console.print("\n[bold]Token Usage:[/bold]")
        console.print(f"  Input tokens: {report.total_input_tokens:,}")
        console.print(f"  Output tokens: {report.total_output_tokens:,}")
        console.print(f"  Total tokens: {report.total_tokens:,}")
        console.print(f"  Average per paper: {report.average_tokens_per_paper:.1f}")

        if report.total_cost > 0:
            console.print("\n[bold]Cost:[/bold]")
            console.print(f"  Total: ${report.total_cost:.4f} USD")
            console.print(
                f"  Per paper: ${report.total_cost / max(report.successful_papers, 1):.4f} USD"
            )
        else:
            console.print("\n[yellow]Cost information not available[/yellow]")


def load_usage_report(filepath: str) -> UsageReport:
    """Load usage report from JSON file.

    Args:
        filepath: Path to the report file

    Returns:
        UsageReport object
    """
    with open(filepath) as f:
        data = json.load(f)

    # Convert string costs back to Decimal, default to 0 if missing
    if "total_cost" in data:
        data["total_cost"] = Decimal(str(data["total_cost"]))
    else:
        data["total_cost"] = Decimal("0.0")

    for usage in data.get("paper_usages", []):
        if "estimated_cost" in usage and usage["estimated_cost"]:
            usage["estimated_cost"] = Decimal(str(usage["estimated_cost"]))

    return UsageReport(**data)
