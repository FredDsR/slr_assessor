"""Logic for comparing evaluations and calculating Cohen's Kappa."""

from typing import List, Tuple
from ..models import EvaluationResult, ConflictReport, Conflict


def identify_conflicts(
    eval1: List[EvaluationResult], eval2: List[EvaluationResult]
) -> Tuple[List[Conflict], List[str], List[str]]:
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
                )
            )

    return conflicts, decisions1, decisions2


def calculate_cohen_kappa(decisions1: List[str], decisions2: List[str]) -> float:
    """Calculate Cohen's Kappa score for agreement between two evaluations.

    Args:
        decisions1: List of decisions from first evaluation
        decisions2: List of decisions from second evaluation

    Returns:
        Cohen's Kappa score
    """
    if not decisions1 or not decisions2 or len(decisions1) != len(decisions2):
        return 0.0

    # Get unique categories
    categories = sorted(list(set(decisions1 + decisions2)))
    n_categories = len(categories)
    n = len(decisions1)

    if n == 0:
        return 0.0

    # Create category to index mapping
    cat_to_idx = {cat: i for i, cat in enumerate(categories)}

    # Build confusion matrix
    confusion_matrix = [[0 for _ in range(n_categories)] for _ in range(n_categories)]

    for d1, d2 in zip(decisions1, decisions2):
        i = cat_to_idx[d1]
        j = cat_to_idx[d2]
        confusion_matrix[i][j] += 1

    # Calculate observed agreement (p_o)
    p_o = sum(confusion_matrix[i][i] for i in range(n_categories)) / n

    # Calculate expected agreement (p_e)
    marginal_1 = [sum(confusion_matrix[i]) for i in range(n_categories)]
    marginal_2 = [
        sum(confusion_matrix[i][j] for i in range(n_categories))
        for j in range(n_categories)
    ]

    p_e = sum((marginal_1[i] / n) * (marginal_2[i] / n) for i in range(n_categories))

    # Calculate Cohen's Kappa
    if p_e == 1.0:
        return 0.0

    kappa = (p_o - p_e) / (1 - p_e)
    return kappa


def compare_evaluations(
    eval1: List[EvaluationResult], eval2: List[EvaluationResult]
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
    )
