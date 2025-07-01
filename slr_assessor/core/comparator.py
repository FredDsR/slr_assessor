"""Logic for comparing evaluations and calculating Cohen's Kappa."""

from sklearn.metrics import cohen_kappa_score

from ..models import Conflict, ConflictReport, EvaluationResult


def identify_conflicts(
    eval1: list[EvaluationResult], eval2: list[EvaluationResult]
) -> tuple[list[Conflict], list[str], list[str]]:
    """Identify conflicts between two evaluation lists.

    Args:
        eval1: First list of evaluation results
        eval2: Second list of evaluation results

    Returns:
        Tuple of (conflicts, decisions1, decisions2) for Kappa calculation
    """
    # Create lookup dictionaries for faster access
    eval1_dict = {result.id: result for result in eval1}
    eval2_dict = {result.id: result for result in eval2}

    # Find common paper IDs
    common_ids = set(eval1_dict.keys()) & set(eval2_dict.keys())

    conflicts = []
    decisions1 = []
    decisions2 = []

    for paper_id in common_ids:
        result1 = eval1_dict[paper_id]
        result2 = eval2_dict[paper_id]

        # Store decisions for Kappa calculation
        decisions1.append(result1.decision)
        decisions2.append(result2.decision)

        # Check for conflicts
        decision_conflict = result1.decision != result2.decision
        score_diff = abs(result1.total_score - result2.total_score)
        score_conflict = score_diff >= 1.0

        if decision_conflict or score_conflict:
            conflicts.append(
                Conflict(
                    id=paper_id,
                    decision_1=result1.decision,
                    decision_2=result2.decision,
                    total_score_1=result1.total_score,
                    total_score_2=result2.total_score,
                    score_difference=score_diff,
                    prompt_version_1=getattr(result1, 'prompt_version', 'unknown'),
                    prompt_version_2=getattr(result2, 'prompt_version', 'unknown'),
                )
            )

    return conflicts, decisions1, decisions2


def calculate_cohen_kappa(decisions1: list[str], decisions2: list[str]) -> float:
    """Calculate Cohen's Kappa score for agreement between two evaluations.

    Args:
        decisions1: List of decisions from first evaluation
        decisions2: List of decisions from second evaluation

    Returns:
        Cohen's Kappa score
    """
    if not decisions1 or not decisions2 or len(decisions1) != len(decisions2):
        return 0.0

    if len(decisions1) == 0:
        return 0.0

    # Handle single item case
    if len(decisions1) == 1:
        return 1.0 if decisions1[0] == decisions2[0] else 0.0

    # Handle perfect agreement case
    if decisions1 == decisions2:
        return 1.0

    # Handle all same labels case (e.g., all "Include")
    unique_1 = set(decisions1)
    unique_2 = set(decisions2)
    if len(unique_1) == 1 and len(unique_2) == 1:
        if unique_1 == unique_2:
            return 1.0  # Perfect agreement
        else:
            return -1.0  # Complete disagreement

    # Use scikit-learn's cohen_kappa_score function
    try:
        kappa = cohen_kappa_score(decisions1, decisions2)
        # Handle NaN cases
        if kappa != kappa:  # Check for NaN
            return 0.0
        return kappa
    except Exception:
        # Fallback to 0.0 if calculation fails
        return 0.0


def compare_evaluations(
    eval1: list[EvaluationResult], eval2: list[EvaluationResult]
) -> ConflictReport:
    """Compare two evaluation lists and generate a conflict report.

    Args:
        eval1: First list of evaluation results
        eval2: Second list of evaluation results

    Returns:
        ConflictReport with conflicts and Cohen's Kappa score
    """
    conflicts, decisions1, decisions2 = identify_conflicts(eval1, eval2)
    kappa_score = calculate_cohen_kappa(decisions1, decisions2)

    return ConflictReport(
        total_papers_compared=len(decisions1),
        total_conflicts=len(conflicts),
        cohen_kappa_score=kappa_score,
        conflicts=conflicts,
        metadata={
            "prompt_versions": {
                "eval1": list(set(getattr(e, 'prompt_version', 'unknown') for e in eval1)),
                "eval2": list(set(getattr(e, 'prompt_version', 'unknown') for e in eval2))
            }
        }
    )
