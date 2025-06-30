"""Fixtures and test utilities."""

import pytest
from decimal import Decimal
from datetime import datetime
from slr_assessor.models import (
    Paper,
    EvaluationResult,
    QAResponseItem,
    LLMAssessment,
    TokenUsage,
    CostEstimate,
    UsageReport,
    Conflict,
    ConflictReport,
    BackupSession,
)


@pytest.fixture
def sample_paper():
    """Create a sample paper for testing."""
    return Paper(
        id="paper_001",
        title="Sample Paper Title",
        abstract="This is a sample abstract for testing purposes.",
    )


@pytest.fixture
def sample_papers():
    """Create a list of sample papers for testing."""
    return [
        Paper(
            id="paper_001",
            title="First Paper",
            abstract="First abstract for testing.",
        ),
        Paper(
            id="paper_002",
            title="Second Paper",
            abstract="Second abstract for testing.",
        ),
        Paper(
            id="paper_003",
            title="Third Paper",
            abstract="Third abstract for testing.",
        ),
    ]


@pytest.fixture
def sample_qa_scores():
    """Create sample QA scores for testing."""
    return {
        "qa1": 1.0,
        "qa2": 0.5,
        "qa3": 1.0,
        "qa4": 0.0,
    }


@pytest.fixture
def sample_qa_reasons():
    """Create sample QA reasons for testing."""
    return {
        "qa1": "Paper meets inclusion criteria clearly.",
        "qa2": "Partially relevant methodology.",
        "qa3": "Strong research design.",
        "qa4": "Limited scope for current review.",
    }


@pytest.fixture
def sample_evaluation_result():
    """Create a sample evaluation result for testing."""
    return EvaluationResult(
        id="paper_001",
        title="Sample Paper Title",
        abstract="This is a sample abstract for testing purposes.",
        qa1_score=1.0,
        qa1_reason="Paper meets inclusion criteria clearly.",
        qa2_score=0.5,
        qa2_reason="Partially relevant methodology.",
        qa3_score=1.0,
        qa3_reason="Strong research design.",
        qa4_score=0.0,
        qa4_reason="Limited scope for current review.",
        total_score=2.5,
        decision="Include",
        llm_summary="Overall positive assessment with minor concerns.",
    )


@pytest.fixture
def sample_evaluation_results():
    """Create a list of sample evaluation results for testing."""
    return [
        EvaluationResult(
            id="paper_001",
            title="First Paper",
            abstract="First abstract.",
            qa1_score=1.0,
            qa1_reason="Strong relevance.",
            qa2_score=1.0,
            qa2_reason="Excellent methodology.",
            qa3_score=1.0,
            qa3_reason="Clear design.",
            qa4_score=1.0,
            qa4_reason="Perfect scope.",
            total_score=4.0,
            decision="Include",
        ),
        EvaluationResult(
            id="paper_002",
            title="Second Paper",
            abstract="Second abstract.",
            qa1_score=0.0,
            qa1_reason="Not relevant.",
            qa2_score=0.0,
            qa2_reason="Poor methodology.",
            qa3_score=0.5,
            qa3_reason="Weak design.",
            qa4_score=0.0,
            qa4_reason="Out of scope.",
            total_score=0.5,
            decision="Exclude",
        ),
        EvaluationResult(
            id="paper_003",
            title="Third Paper",
            abstract="Third abstract.",
            qa1_score=1.0,
            qa1_reason="Good relevance.",
            qa2_score=0.5,
            qa2_reason="Adequate methodology.",
            qa3_score=1.0,
            qa3_reason="Solid design.",
            qa4_score=0.0,
            qa4_reason="Limited scope.",
            total_score=2.5,
            decision="Include",
        ),
    ]


@pytest.fixture
def sample_qa_response_items():
    """Create sample QA response items for testing."""
    return [
        QAResponseItem(
            qa_id="qa1",
            question="Is this paper relevant?",
            score=1.0,
            reason="Highly relevant to the research question.",
        ),
        QAResponseItem(
            qa_id="qa2",
            question="Is the methodology sound?",
            score=0.5,
            reason="Methodology has some limitations.",
        ),
    ]


@pytest.fixture
def sample_llm_assessment():
    """Create a sample LLM assessment for testing."""
    return LLMAssessment(
        assessments=[
            QAResponseItem(
                qa_id="qa1",
                question="Is this paper relevant?",
                score=1.0,
                reason="Highly relevant to the research question.",
            ),
            QAResponseItem(
                qa_id="qa2",
                question="Is the methodology sound?",
                score=0.5,
                reason="Methodology has some limitations.",
            ),
        ],
        overall_summary="Paper is relevant but has methodological concerns.",
    )


@pytest.fixture
def sample_token_usage():
    """Create sample token usage for testing."""
    return TokenUsage(
        input_tokens=1000,
        output_tokens=500,
        total_tokens=1500,
        model="gpt-4",
        provider="openai",
        estimated_cost=Decimal("0.045"),
    )


@pytest.fixture
def sample_cost_estimate():
    """Create sample cost estimate for testing."""
    return CostEstimate(
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


@pytest.fixture
def sample_usage_report():
    """Create sample usage report for testing."""
    return UsageReport(
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


@pytest.fixture
def sample_conflict():
    """Create sample conflict for testing."""
    return Conflict(
        id="paper_001",
        decision_1="Include",
        decision_2="Exclude",
        total_score_1=2.5,
        total_score_2=1.0,
        score_difference=1.5,
    )


@pytest.fixture
def sample_conflict_report():
    """Create sample conflict report for testing."""
    return ConflictReport(
        total_papers_compared=100,
        total_conflicts=5,
        cohen_kappa_score=0.85,
        conflicts=[
            Conflict(
                id="paper_001",
                decision_1="Include",
                decision_2="Exclude",
                total_score_1=2.5,
                total_score_2=1.0,
                score_difference=1.5,
            )
        ],
    )


@pytest.fixture
def sample_backup_session():
    """Create sample backup session for testing."""
    return BackupSession(
        session_id="backup_001",
        start_time="2025-01-01T10:00:00",
        provider="openai",
        model="gpt-4",
        input_csv_path="/path/to/input.csv",
        output_csv_path="/path/to/output.csv",
        total_papers=100,
        processed_papers=[],
        failed_papers=[],
        processed_paper_ids=[],
        last_updated="2025-01-01T10:00:00",
    )
