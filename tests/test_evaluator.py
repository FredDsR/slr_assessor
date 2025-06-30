"""Tests for the core evaluator module."""

import pytest
from slr_assessor.core.evaluator import calculate_decision, create_evaluation_result


def test_calculate_decision_include():
    """Test that scores >= 2.5 result in Include decision."""
    assert calculate_decision(2.5) == "Include"
    assert calculate_decision(3.0) == "Include"
    assert calculate_decision(4.0) == "Include"
    assert calculate_decision(2.6) == "Include"


def test_calculate_decision_conditional_review():
    """Test that scores between 1.5 and 2.5 result in Conditional Review."""
    assert calculate_decision(1.5) == "Conditional Review"
    assert calculate_decision(2.0) == "Conditional Review"
    assert calculate_decision(2.4) == "Conditional Review"
    assert calculate_decision(1.9) == "Conditional Review"


def test_calculate_decision_exclude():
    """Test that scores < 1.5 result in Exclude decision."""
    assert calculate_decision(0.0) == "Exclude"
    assert calculate_decision(1.0) == "Exclude"
    assert calculate_decision(1.4) == "Exclude"
    assert calculate_decision(0.5) == "Exclude"


def test_calculate_decision_edge_cases():
    """Test edge cases for decision boundaries."""
    # Exact boundary values
    assert calculate_decision(2.5) == "Include"
    assert calculate_decision(1.5) == "Conditional Review"

    # Just below boundaries
    assert calculate_decision(2.49) == "Conditional Review"
    assert calculate_decision(1.49) == "Exclude"


def test_create_basic_evaluation_result(sample_qa_scores, sample_qa_reasons):
    """Test creating a basic evaluation result."""
    result = create_evaluation_result(
        paper_id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa_scores=sample_qa_scores,
        qa_reasons=sample_qa_reasons,
    )

    assert result.id == "paper_001"
    assert result.title == "Test Paper"
    assert result.abstract == "Test abstract"
    assert result.qa1_score == 1.0
    assert result.qa2_score == 0.5
    assert result.qa3_score == 1.0
    assert result.qa4_score == 0.0
    assert result.total_score == 2.5
    assert result.decision == "Include"
    assert result.llm_summary is None
    assert result.error is None


def test_create_evaluation_result_with_llm_summary(sample_qa_scores, sample_qa_reasons):
    """Test creating evaluation result with LLM summary."""
    result = create_evaluation_result(
        paper_id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa_scores=sample_qa_scores,
        qa_reasons=sample_qa_reasons,
        llm_summary="Overall positive assessment",
    )

    assert result.llm_summary == "Overall positive assessment"


def test_create_evaluation_result_with_error(sample_qa_scores, sample_qa_reasons):
    """Test creating evaluation result with error message."""
    result = create_evaluation_result(
        paper_id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa_scores=sample_qa_scores,
        qa_reasons=sample_qa_reasons,
        error="Processing failed",
    )

    assert result.error == "Processing failed"


def test_create_evaluation_result_total_score_calculation():
    """Test that total score is correctly calculated."""
    qa_scores = {"qa1": 0.5, "qa2": 1.0, "qa3": 0.5, "qa4": 1.0}
    qa_reasons = {"qa1": "test", "qa2": "test", "qa3": "test", "qa4": "test"}

    result = create_evaluation_result(
        paper_id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa_scores=qa_scores,
        qa_reasons=qa_reasons,
    )

    assert result.total_score == 3.0
    assert result.decision == "Include"


def test_create_evaluation_result_exclude_decision():
    """Test evaluation result with exclude decision."""
    qa_scores = {"qa1": 0.0, "qa2": 0.0, "qa3": 0.5, "qa4": 0.0}
    qa_reasons = {"qa1": "poor", "qa2": "poor", "qa3": "weak", "qa4": "poor"}

    result = create_evaluation_result(
        paper_id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa_scores=qa_scores,
        qa_reasons=qa_reasons,
    )

    assert result.total_score == 0.5
    assert result.decision == "Exclude"


def test_create_evaluation_result_conditional_review():
    """Test evaluation result with conditional review decision."""
    qa_scores = {"qa1": 0.5, "qa2": 0.5, "qa3": 0.5, "qa4": 0.5}
    qa_reasons = {"qa1": "okay", "qa2": "okay", "qa3": "okay", "qa4": "okay"}

    result = create_evaluation_result(
        paper_id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa_scores=qa_scores,
        qa_reasons=qa_reasons,
    )

    assert result.total_score == 2.0
    assert result.decision == "Conditional Review"


def test_create_evaluation_result_missing_qa_scores():
    """Test behavior with missing QA scores."""
    qa_scores = {"qa1": 1.0, "qa2": 0.5}  # Missing qa3 and qa4
    qa_reasons = {"qa1": "good", "qa2": "okay", "qa3": "test", "qa4": "test"}

    with pytest.raises(KeyError):
        create_evaluation_result(
            paper_id="paper_001",
            title="Test Paper",
            abstract="Test abstract",
            qa_scores=qa_scores,
            qa_reasons=qa_reasons,
        )


def test_create_evaluation_result_missing_qa_reasons():
    """Test behavior with missing QA reasons."""
    qa_scores = {"qa1": 1.0, "qa2": 0.5, "qa3": 1.0, "qa4": 0.0}
    qa_reasons = {"qa1": "good", "qa2": "okay"}  # Missing qa3 and qa4

    with pytest.raises(KeyError):
        create_evaluation_result(
            paper_id="paper_001",
            title="Test Paper",
            abstract="Test abstract",
            qa_scores=qa_scores,
            qa_reasons=qa_reasons,
        )
