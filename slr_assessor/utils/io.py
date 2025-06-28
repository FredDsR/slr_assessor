"""CSV reading and writing utilities."""

import pandas as pd

from ..models import EvaluationResult, Paper


def read_papers_from_csv(csv_path: str) -> list[Paper]:
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


def read_human_evaluations_from_csv(csv_path: str) -> list[EvaluationResult]:
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


def read_evaluations_from_csv(csv_path: str) -> list[EvaluationResult]:
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
    evaluations: list[EvaluationResult], csv_path: str
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
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "estimated_cost",
                "model",
                "provider",
            ]
        )
    else:
        # Convert to DataFrame
        data = []
        for eval_result in evaluations:
            row_data = {
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

            # Add token usage information if available
            if eval_result.token_usage:
                row_data.update(
                    {
                        "input_tokens": eval_result.token_usage.input_tokens,
                        "output_tokens": eval_result.token_usage.output_tokens,
                        "total_tokens": eval_result.token_usage.total_tokens,
                        "estimated_cost": float(eval_result.token_usage.estimated_cost)
                        if eval_result.token_usage.estimated_cost
                        else None,
                        "model": eval_result.token_usage.model,
                        "provider": eval_result.token_usage.provider,
                    }
                )
            else:
                row_data.update(
                    {
                        "input_tokens": None,
                        "output_tokens": None,
                        "total_tokens": None,
                        "estimated_cost": None,
                        "model": None,
                        "provider": None,
                    }
                )

            data.append(row_data)
        df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(csv_path, index=False)
