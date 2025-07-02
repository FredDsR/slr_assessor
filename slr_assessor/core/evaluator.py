"""Core logic for scoring and decision making."""

from ..models import EvaluationResult


def calculate_decision(total_score: float) -> str:
    """Calculate decision based on total score using the defined thresholds.

    Args:
        total_score: The sum of all QA scores (0-4 range)

    Returns:
        Decision string: "Include", "Conditional Review", or "Exclude"
    """
    if total_score >= 2.5:
        return "Include"
    elif total_score >= 1.5:
        return "Conditional Review"
    else:
        return "Exclude"


def create_evaluation_result(
    paper_id: str,
    title: str,
    abstract: str,
    qa_scores: dict[str, float],
    qa_reasons: dict[str, str],
    llm_summary: str = None,
    error: str = None,
    prompt_version: str = "v1.0",
    prompt_hash: str = None,
) -> EvaluationResult:
    """Create an EvaluationResult with calculated totals and decision.

    Args:
        paper_id: Unique paper identifier
        title: Paper title
        abstract: Paper abstract
        qa_scores: Dictionary with keys 'qa1', 'qa2', 'qa3', 'qa4' and float values
        qa_reasons: Dictionary with keys 'qa1', 'qa2', 'qa3', 'qa4' and reason strings
        llm_summary: Optional summary from LLM assessment
        error: Optional error message if processing failed
        prompt_version: Version of prompt used for evaluation
        prompt_hash: Hash of prompt for exact identification

    Returns:
        EvaluationResult with calculated total_score and decision
    """
    # Calculate total score
    total_score = sum(qa_scores.values())

    # Determine decision
    decision = calculate_decision(total_score)

    return EvaluationResult(
        id=paper_id,
        title=title,
        abstract=abstract,
        qa1_score=qa_scores["qa1"],
        qa1_reason=qa_reasons["qa1"],
        qa2_score=qa_scores["qa2"],
        qa2_reason=qa_reasons["qa2"],
        qa3_score=qa_scores["qa3"],
        qa3_reason=qa_reasons["qa3"],
        qa4_score=qa_scores["qa4"],
        qa4_reason=qa_reasons["qa4"],
        total_score=total_score,
        decision=decision,
        llm_summary=llm_summary,
        error=error,
        prompt_version=prompt_version,
        prompt_hash=prompt_hash,
    )
