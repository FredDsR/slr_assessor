"""Tests for the data models."""

import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError
from slr_assessor.models import (
    Paper,
    QAResponseItem,
    LLMAssessment,
    TokenUsage,
    CostEstimate,
    UsageReport,
    EvaluationResult,
    Conflict,
    ConflictReport,
    BackupSession,
)


def test_paper_valid_creation():
    """Test creating a valid paper."""
    paper = Paper(
        id="test_001",
        title="Test Paper",
        abstract="This is a test abstract.",
    )
    assert paper.id == "test_001"
    assert paper.title == "Test Paper"
    assert paper.abstract == "This is a test abstract."


def test_paper_missing_required_fields():
    """Test that missing required fields raise validation errors."""
    with pytest.raises(ValidationError):
        Paper(title="Test Paper", abstract="Test abstract")

    with pytest.raises(ValidationError):
        Paper(id="test_001", abstract="Test abstract")

    with pytest.raises(ValidationError):
        Paper(id="test_001", title="Test Paper")


def test_qa_response_valid_creation():
    """Test creating a valid QA response item."""
    qa_response = QAResponseItem(
        qa_id="qa1",
        question="Is this paper relevant?",
        score=1.0,
        reason="Highly relevant to the research question.",
    )
    assert qa_response.qa_id == "qa1"
    assert qa_response.question == "Is this paper relevant?"
    assert qa_response.score == 1.0
    assert qa_response.reason == "Highly relevant to the research question."


def test_qa_response_valid_scores():
    """Test that valid scores (0, 0.5, 1) are accepted."""
    for score in [0, 0.5, 1.0]:
        qa_response = QAResponseItem(
            qa_id="qa1",
            question="Test question",
            score=score,
            reason="Test reason",
        )
        assert qa_response.score == score


def test_qa_response_missing_fields():
    """Test that missing required fields raise validation errors."""
    with pytest.raises(ValidationError):
        QAResponseItem(
            question="Test question", score=1.0, reason="Test reason"
        )


def test_llm_assessment_valid_creation(sample_qa_response_items):
    """Test creating a valid LLM assessment."""
    assessment = LLMAssessment(
        assessments=sample_qa_response_items,
        overall_summary="Test summary",
    )
    assert len(assessment.assessments) == 2
    assert assessment.overall_summary == "Test summary"


def test_llm_assessment_empty_assessments():
    """Test creating LLM assessment with empty assessments list."""
    assessment = LLMAssessment(
        assessments=[],
        overall_summary="Test summary",
    )
    assert len(assessment.assessments) == 0
    assert assessment.overall_summary == "Test summary"


def test_token_usage_valid_creation():
    """Test creating a valid token usage object."""
    usage = TokenUsage(
        input_tokens=1000,
        output_tokens=500,
        total_tokens=1500,
        model="gpt-4",
        provider="openai",
        estimated_cost=Decimal("0.045"),
    )
    assert usage.input_tokens == 1000
    assert usage.output_tokens == 500
    assert usage.total_tokens == 1500
    assert usage.model == "gpt-4"
    assert usage.provider == "openai"
    assert usage.estimated_cost == Decimal("0.045")


def test_token_usage_without_cost():
    """Test creating token usage without estimated cost."""
    usage = TokenUsage(
        input_tokens=1000,
        output_tokens=500,
        total_tokens=1500,
        model="gpt-4",
        provider="openai",
    )
    assert usage.estimated_cost is None


def test_token_usage_negative_values():
    """Test that negative token values are handled."""
    # Pydantic doesn't enforce positive integers by default
    usage = TokenUsage(
        input_tokens=-100,
        output_tokens=500,
        total_tokens=400,
        model="gpt-4",
        provider="openai",
    )
    assert usage.input_tokens == -100


def test_cost_estimate_valid_creation():
    """Test creating a valid cost estimate."""
    estimate = CostEstimate(
        total_papers=100,
        estimated_input_tokens_per_paper=1000,
        estimated_output_tokens_per_paper=500,
        estimated_total_tokens=150000,
        estimated_total_cost=Decimal("4.50"),
        cost_per_input_token=Decimal("0.00003"),
        cost_per_output_token=Decimal("0.00006"),
        provider="openai",
        model="gpt-4",
    )
    assert estimate.total_papers == 100
    assert estimate.estimated_total_cost == Decimal("4.50")


def test_usage_report_valid_creation():
    """Test creating a valid usage report."""
    report = UsageReport(
        session_id="session_001",
        start_time="2025-01-01T10:00:00",
        end_time="2025-01-01T11:00:00",
        provider="openai",
        model="gpt-4",
        total_papers_processed=10,
        successful_papers=9,
        failed_papers=1,
        total_input_tokens=10000,
        total_output_tokens=5000,
        total_tokens=15000,
        total_cost=Decimal("0.45"),
        average_tokens_per_paper=1500.0,
    )
    assert report.session_id == "session_001"
    assert report.total_papers_processed == 10
    assert report.successful_papers == 9
    assert report.failed_papers == 1


def test_usage_report_without_end_time():
    """Test creating usage report without end time."""
    report = UsageReport(
        session_id="session_001",
        start_time="2025-01-01T10:00:00",
        provider="openai",
        model="gpt-4",
        total_papers_processed=10,
        successful_papers=9,
        failed_papers=1,
        total_input_tokens=10000,
        total_output_tokens=5000,
        total_tokens=15000,
        total_cost=Decimal("0.45"),
        average_tokens_per_paper=1500.0,
    )
    assert report.end_time is None


def test_evaluation_result_valid_creation():
    """Test creating a valid evaluation result."""
    result = EvaluationResult(
        id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa1_score=1.0,
        qa1_reason="Good reason",
        qa2_score=0.5,
        qa2_reason="Okay reason",
        qa3_score=1.0,
        qa3_reason="Strong reason",
        qa4_score=0.0,
        qa4_reason="Weak reason",
        total_score=2.5,
        decision="Include",
    )
    assert result.id == "paper_001"
    assert result.total_score == 2.5
    assert result.decision == "Include"


def test_evaluation_result_with_optional_fields(sample_token_usage):
    """Test creating evaluation result with optional fields."""
    result = EvaluationResult(
        id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa1_score=1.0,
        qa1_reason="Good reason",
        qa2_score=0.5,
        qa2_reason="Okay reason",
        qa3_score=1.0,
        qa3_reason="Strong reason",
        qa4_score=0.0,
        qa4_reason="Weak reason",
        total_score=2.5,
        decision="Include",
        llm_summary="Overall good paper",
        error=None,
        token_usage=sample_token_usage,
    )
    assert result.llm_summary == "Overall good paper"
    assert result.error is None
    assert result.token_usage is not None


def test_evaluation_result_with_error():
    """Test creating evaluation result with error."""
    result = EvaluationResult(
        id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa1_score=0.0,
        qa1_reason="",
        qa2_score=0.0,
        qa2_reason="",
        qa3_score=0.0,
        qa3_reason="",
        qa4_score=0.0,
        qa4_reason="",
        total_score=0.0,
        decision="Exclude",
        error="Failed to process paper",
    )
    assert result.error == "Failed to process paper"


def test_conflict_valid_creation():
    """Test creating a valid conflict."""
    conflict = Conflict(
        id="paper_001",
        decision_1="Include",
        decision_2="Exclude",
        total_score_1=2.5,
        total_score_2=1.0,
        score_difference=1.5,
    )
    assert conflict.id == "paper_001"
    assert conflict.decision_1 == "Include"
    assert conflict.decision_2 == "Exclude"
    assert conflict.score_difference == 1.5


def test_conflict_report_valid_creation(sample_conflict):
    """Test creating a valid conflict report."""
    report = ConflictReport(
        total_papers_compared=100,
        total_conflicts=5,
        cohen_kappa_score=0.85,
        conflicts=[sample_conflict],
    )
    assert report.total_papers_compared == 100
    assert report.total_conflicts == 5
    assert report.cohen_kappa_score == 0.85
    assert len(report.conflicts) == 1


def test_conflict_report_empty_conflicts():
    """Test creating conflict report with no conflicts."""
    report = ConflictReport(
        total_papers_compared=100,
        total_conflicts=0,
        cohen_kappa_score=1.0,
        conflicts=[],
    )
    assert report.total_conflicts == 0
    assert len(report.conflicts) == 0


def test_backup_session_valid_creation():
    """Test creating a valid backup session."""
    session = BackupSession(
        session_id="backup_001",
        start_time="2025-01-01T10:00:00",
        provider="openai",
        model="gpt-4",
        input_csv_path="/path/to/input.csv",
        output_csv_path="/path/to/output.csv",
        total_papers=100,
        last_updated="2025-01-01T10:00:00",
    )
    assert session.session_id == "backup_001"
    assert session.total_papers == 100
    assert len(session.processed_papers) == 0
    assert len(session.failed_papers) == 0


def test_backup_session_add_processed_paper(sample_evaluation_result):
    """Test adding a processed paper to backup session."""
    session = BackupSession(
        session_id="backup_001",
        start_time="2025-01-01T10:00:00",
        provider="openai",
        model="gpt-4",
        input_csv_path="/path/to/input.csv",
        output_csv_path="/path/to/output.csv",
        total_papers=100,
        last_updated="2025-01-01T10:00:00",
    )

    session.add_processed_paper(sample_evaluation_result)

    assert len(session.processed_papers) == 1
    assert session.processed_papers[0].id == "paper_001"
    assert sample_evaluation_result.id in session.processed_paper_ids
    assert session.is_paper_processed("paper_001")


def test_backup_session_add_duplicate_paper(sample_evaluation_result):
    """Test adding the same paper twice doesn't duplicate."""
    session = BackupSession(
        session_id="backup_001",
        start_time="2025-01-01T10:00:00",
        provider="openai",
        model="gpt-4",
        input_csv_path="/path/to/input.csv",
        output_csv_path="/path/to/output.csv",
        total_papers=100,
        last_updated="2025-01-01T10:00:00",
    )

    session.add_processed_paper(sample_evaluation_result)
    session.add_processed_paper(sample_evaluation_result)

    assert len(session.processed_papers) == 1
    assert len(session.processed_paper_ids) == 1


def test_backup_session_add_failed_paper(sample_evaluation_result):
    """Test adding a failed paper to backup session."""
    session = BackupSession(
        session_id="backup_001",
        start_time="2025-01-01T10:00:00",
        provider="openai",
        model="gpt-4",
        input_csv_path="/path/to/input.csv",
        output_csv_path="/path/to/output.csv",
        total_papers=100,
        last_updated="2025-01-01T10:00:00",
    )

    session.add_failed_paper(sample_evaluation_result)

    assert len(session.failed_papers) == 1
    assert session.failed_papers[0].id == "paper_001"
    # Failed papers are not marked as processed
    assert not session.is_paper_processed("paper_001")


def test_backup_session_get_remaining_papers(sample_papers, sample_evaluation_result):
    """Test getting remaining unprocessed papers."""
    session = BackupSession(
        session_id="backup_001",
        start_time="2025-01-01T10:00:00",
        provider="openai",
        model="gpt-4",
        input_csv_path="/path/to/input.csv",
        output_csv_path="/path/to/output.csv",
        total_papers=3,
        last_updated="2025-01-01T10:00:00",
    )

    # Add one processed paper
    session.add_processed_paper(sample_evaluation_result)

    # Get remaining papers
    remaining = session.get_remaining_papers(sample_papers)

    assert len(remaining) == 2
    remaining_ids = [paper.id for paper in remaining]
    assert "paper_001" not in remaining_ids
    assert "paper_002" in remaining_ids
    assert "paper_003" in remaining_ids
