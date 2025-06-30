"""Tests for the core comparator module."""

from slr_assessor.core.comparator import (
    calculate_cohen_kappa,
    compare_evaluations,
    identify_conflicts,
)
from slr_assessor.models import ConflictReport, EvaluationResult


def test_identify_conflicts_no_conflicts():
    """Test when there are no conflicts between evaluations."""
    eval1 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=1.0,
            qa3_reason="Good",
            qa4_score=1.0,
            qa4_reason="Good",
            total_score=4.0,
            decision="Include",
        )
    ]

    eval2 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=1.0,
            qa3_reason="Good",
            qa4_score=1.0,
            qa4_reason="Good",
            total_score=4.0,
            decision="Include",
        )
    ]

    conflicts, decisions1, decisions2 = identify_conflicts(eval1, eval2)

    assert len(conflicts) == 0
    assert decisions1 == ["Include"]
    assert decisions2 == ["Include"]


def test_identify_conflicts_decision_conflict():
    """Test when there's a decision conflict."""
    eval1 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=0.5,
            qa3_reason="Okay",
            qa4_score=0.0,
            qa4_reason="Poor",
            total_score=2.5,
            decision="Include",
        )
    ]

    eval2 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=0.5,
            qa1_reason="Okay",
            qa2_score=0.5,
            qa2_reason="Okay",
            qa3_score=0.5,
            qa3_reason="Okay",
            qa4_score=0.0,
            qa4_reason="Poor",
            total_score=1.5,
            decision="Conditional Review",
        )
    ]

    conflicts, decisions1, decisions2 = identify_conflicts(eval1, eval2)

    assert len(conflicts) == 1
    assert conflicts[0].id == "paper_001"
    assert conflicts[0].decision_1 == "Include"
    assert conflicts[0].decision_2 == "Conditional Review"
    assert conflicts[0].score_difference == 1.0


def test_identify_conflicts_score_conflict_same_decision():
    """Test when there's a significant score difference but same decision."""
    eval1 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=1.0,
            qa3_reason="Good",
            qa4_score=1.0,
            qa4_reason="Good",
            total_score=4.0,
            decision="Include",
        )
    ]

    eval2 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=0.5,
            qa3_reason="Okay",
            qa4_score=0.5,
            qa4_reason="Okay",
            total_score=3.0,
            decision="Include",
        )
    ]

    conflicts, decisions1, decisions2 = identify_conflicts(eval1, eval2)

    assert len(conflicts) == 1
    assert conflicts[0].score_difference == 1.0
    assert conflicts[0].decision_1 == "Include"
    assert conflicts[0].decision_2 == "Include"


def test_identify_conflicts_multiple_papers():
    """Test multiple papers with some conflicts."""
    eval1 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=1.0,
            qa3_reason="Good",
            qa4_score=1.0,
            qa4_reason="Good",
            total_score=4.0,
            decision="Include",
        ),
        EvaluationResult(
            id="paper_002",
            title="Paper 2",
            abstract="Abstract 2",
            qa1_score=0.0,
            qa1_reason="Poor",
            qa2_score=0.0,
            qa2_reason="Poor",
            qa3_score=0.0,
            qa3_reason="Poor",
            qa4_score=0.0,
            qa4_reason="Poor",
            total_score=0.0,
            decision="Exclude",
        ),
    ]

    eval2 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=1.0,
            qa3_reason="Good",
            qa4_score=1.0,
            qa4_reason="Good",
            total_score=4.0,
            decision="Include",
        ),
        EvaluationResult(
            id="paper_002",
            title="Paper 2",
            abstract="Abstract 2",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=0.5,
            qa3_reason="Okay",
            qa4_score=0.0,
            qa4_reason="Poor",
            total_score=2.5,
            decision="Include",
        ),
    ]

    conflicts, decisions1, decisions2 = identify_conflicts(eval1, eval2)

    assert len(conflicts) == 1
    assert conflicts[0].id == "paper_002"
    assert len(decisions1) == 2
    assert len(decisions2) == 2


def test_identify_conflicts_no_common_papers():
    """Test when there are no common papers between evaluations."""
    eval1 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=1.0,
            qa3_reason="Good",
            qa4_score=1.0,
            qa4_reason="Good",
            total_score=4.0,
            decision="Include",
        )
    ]

    eval2 = [
        EvaluationResult(
            id="paper_002",
            title="Paper 2",
            abstract="Abstract 2",
            qa1_score=0.0,
            qa1_reason="Poor",
            qa2_score=0.0,
            qa2_reason="Poor",
            qa3_score=0.0,
            qa3_reason="Poor",
            qa4_score=0.0,
            qa4_reason="Poor",
            total_score=0.0,
            decision="Exclude",
        )
    ]

    conflicts, decisions1, decisions2 = identify_conflicts(eval1, eval2)

    assert len(conflicts) == 0
    assert len(decisions1) == 0
    assert len(decisions2) == 0


def test_identify_conflicts_empty_evaluations():
    """Test with empty evaluation lists."""
    conflicts, decisions1, decisions2 = identify_conflicts([], [])

    assert len(conflicts) == 0
    assert len(decisions1) == 0
    assert len(decisions2) == 0


def test_calculate_cohen_kappa_perfect_agreement():
    """Test perfect agreement (kappa = 1.0)."""
    decisions1 = ["Include", "Exclude", "Conditional Review"]
    decisions2 = ["Include", "Exclude", "Conditional Review"]

    kappa = calculate_cohen_kappa(decisions1, decisions2)
    assert kappa == 1.0


def test_calculate_cohen_kappa_no_agreement():
    """Test no agreement scenario."""
    decisions1 = ["Include", "Include", "Include"]
    decisions2 = ["Exclude", "Exclude", "Exclude"]

    kappa = calculate_cohen_kappa(decisions1, decisions2)
    assert kappa < 0  # Negative kappa indicates systematic disagreement


def test_calculate_cohen_kappa_partial_agreement():
    """Test partial agreement scenario."""
    decisions1 = ["Include", "Include", "Include", "Exclude"]
    decisions2 = ["Include", "Include", "Exclude", "Exclude"]

    kappa = calculate_cohen_kappa(decisions1, decisions2)
    assert 0 < kappa < 1


def test_calculate_cohen_kappa_empty_lists():
    """Test with empty decision lists."""
    kappa = calculate_cohen_kappa([], [])
    assert kappa == 0.0


def test_calculate_cohen_kappa_mismatched_lengths():
    """Test with mismatched list lengths."""
    decisions1 = ["Include", "Exclude"]
    decisions2 = ["Include"]

    kappa = calculate_cohen_kappa(decisions1, decisions2)
    assert kappa == 0.0


def test_calculate_cohen_kappa_single_item():
    """Test with single item lists."""
    decisions1 = ["Include"]
    decisions2 = ["Include"]

    kappa = calculate_cohen_kappa(decisions1, decisions2)
    # Single item should have perfect agreement
    assert kappa == 1.0 or kappa == 0.0  # Depending on implementation


def test_compare_evaluations_complete_comparison(sample_evaluation_results):
    """Test complete comparison with sample data."""
    # Create a second set with some conflicts
    eval2 = [
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
            qa1_score=1.0,
            qa1_reason="Actually relevant.",
            qa2_score=1.0,
            qa2_reason="Good methodology.",
            qa3_score=1.0,
            qa3_reason="Strong design.",
            qa4_score=0.5,
            qa4_reason="Adequate scope.",
            total_score=3.5,
            decision="Include",
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

    report = compare_evaluations(sample_evaluation_results, eval2)

    assert isinstance(report, ConflictReport)
    assert report.total_papers_compared == 3
    assert report.total_conflicts == 1  # paper_002 has a conflict
    assert isinstance(report.cohen_kappa_score, float)
    assert len(report.conflicts) == 1


def test_compare_evaluations_no_conflicts():
    """Test comparison with identical evaluations."""
    eval1 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=1.0,
            qa3_reason="Good",
            qa4_score=1.0,
            qa4_reason="Good",
            total_score=4.0,
            decision="Include",
        )
    ]

    eval2 = [
        EvaluationResult(
            id="paper_001",
            title="Paper 1",
            abstract="Abstract 1",
            qa1_score=1.0,
            qa1_reason="Good",
            qa2_score=1.0,
            qa2_reason="Good",
            qa3_score=1.0,
            qa3_reason="Good",
            qa4_score=1.0,
            qa4_reason="Good",
            total_score=4.0,
            decision="Include",
        )
    ]

    report = compare_evaluations(eval1, eval2)

    assert report.total_papers_compared == 1
    assert report.total_conflicts == 0
    assert report.cohen_kappa_score == 1.0
    assert len(report.conflicts) == 0


def test_compare_evaluations_empty():
    """Test comparison with empty evaluation lists."""
    report = compare_evaluations([], [])

    assert report.total_papers_compared == 0
    assert report.total_conflicts == 0
    assert report.cohen_kappa_score == 0.0
    assert len(report.conflicts) == 0
