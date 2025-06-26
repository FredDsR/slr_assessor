"""CSV reading and writing utilities."""

import pandas as pd
from typing import List
from ..models import Paper, EvaluationResult


def read_papers_from_csv(csv_path: str) -> List[Paper]:
    """Read papers from input CSV file.

    Args:
        csv_path: Path to the CSV file

    Returns:
        List of Paper objects

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Check required columns
    required_columns = {"id", "title", "abstract"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Missing required columns: {missing}")

    # Convert to Paper objects
    papers = []
    for _, row in df.iterrows():
        papers.append(
            Paper(
                id=str(row["id"]),
                title=str(row["title"]),
                abstract=str(row["abstract"]),
            )
        )

    return papers


def read_human_evaluations_from_csv(csv_path: str) -> List[EvaluationResult]:
    """Read human evaluations from CSV file.

    Args:
        csv_path: Path to the CSV file with human evaluations

    Returns:
        List of EvaluationResult objects

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Check required columns
    required_columns = {
        "id",
        "title",
        "abstract",
        "qa1_score",
        "qa1_reason",
        "qa2_score",
        "qa2_reason",
        "qa3_score",
        "qa3_reason",
        "qa4_score",
        "qa4_reason",
    }
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Missing required columns: {missing}")

    # Import here to avoid circular import
    from ..core.evaluator import create_evaluation_result

    # Convert to EvaluationResult objects
    evaluations = []
    for _, row in df.iterrows():
        qa_scores = {
            "qa1": float(row["qa1_score"]),
            "qa2": float(row["qa2_score"]),
            "qa3": float(row["qa3_score"]),
            "qa4": float(row["qa4_score"]),
        }
        qa_reasons = {
            "qa1": str(row["qa1_reason"]),
            "qa2": str(row["qa2_reason"]),
            "qa3": str(row["qa3_reason"]),
            "qa4": str(row["qa4_reason"]),
        }

        evaluation = create_evaluation_result(
            paper_id=str(row["id"]),
            title=str(row["title"]),
            abstract=str(row["abstract"]),
            qa_scores=qa_scores,
            qa_reasons=qa_reasons,
        )
        evaluations.append(evaluation)

    return evaluations


def read_evaluations_from_csv(csv_path: str) -> List[EvaluationResult]:
    """Read evaluations from a processed evaluation CSV file.

    Args:
        csv_path: Path to the evaluation CSV file

    Returns:
        List of EvaluationResult objects

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Check required columns for evaluation results
    required_columns = {
        "id",
        "title",
        "abstract",
        "qa1_score",
        "qa1_reason",
        "qa2_score",
        "qa2_reason",
        "qa3_score",
        "qa3_reason",
        "qa4_score",
        "qa4_reason",
        "total_score",
        "decision",
    }
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Missing required columns: {missing}")

    # Convert to EvaluationResult objects
    evaluations = []
    for _, row in df.iterrows():
        evaluation = EvaluationResult(
            id=str(row["id"]),
            title=str(row["title"]),
            abstract=str(row["abstract"]),
            qa1_score=float(row["qa1_score"]),
            qa1_reason=str(row["qa1_reason"]),
            qa2_score=float(row["qa2_score"]),
            qa2_reason=str(row["qa2_reason"]),
            qa3_score=float(row["qa3_score"]),
            qa3_reason=str(row["qa3_reason"]),
            qa4_score=float(row["qa4_score"]),
            qa4_reason=str(row["qa4_reason"]),
            total_score=float(row["total_score"]),
            decision=str(row["decision"]),
            llm_summary=str(row["llm_summary"])
            if "llm_summary" in row and pd.notna(row["llm_summary"])
            else None,
            error=str(row["error"])
            if "error" in row and pd.notna(row["error"])
            else None,
        )
        evaluations.append(evaluation)

    return evaluations


def write_evaluations_to_csv(
    evaluations: List[EvaluationResult], csv_path: str
) -> None:
    """Write evaluations to CSV file.

    Args:
        evaluations: List of EvaluationResult objects
        csv_path: Path to save the CSV file
    """
    if not evaluations:
        # Create empty CSV with headers
        df = pd.DataFrame(
            columns=[
                "id",
                "title",
                "abstract",
                "qa1_score",
                "qa1_reason",
                "qa2_score",
                "qa2_reason",
                "qa3_score",
                "qa3_reason",
                "qa4_score",
                "qa4_reason",
                "total_score",
                "decision",
                "llm_summary",
                "error",
            ]
        )
    else:
        # Convert to DataFrame
        data = []
        for eval_result in evaluations:
            data.append(
                {
                    "id": eval_result.id,
                    "title": eval_result.title,
                    "abstract": eval_result.abstract,
                    "qa1_score": eval_result.qa1_score,
                    "qa1_reason": eval_result.qa1_reason,
                    "qa2_score": eval_result.qa2_score,
                    "qa2_reason": eval_result.qa2_reason,
                    "qa3_score": eval_result.qa3_score,
                    "qa3_reason": eval_result.qa3_reason,
                    "qa4_score": eval_result.qa4_score,
                    "qa4_reason": eval_result.qa4_reason,
                    "total_score": eval_result.total_score,
                    "decision": eval_result.decision,
                    "llm_summary": eval_result.llm_summary,
                    "error": eval_result.error,
                }
            )
        df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(csv_path, index=False)
