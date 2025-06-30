"""Pydantic data models for the SLR Assessor CLI."""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional, Union

from pydantic import BaseModel


class Paper(BaseModel):
    """Represents a single paper to be screened."""

    id: str
    title: str
    abstract: str


class QAResponseItem(BaseModel):
    """Represents the assessment for a single QA question as returned by the LLM."""

    qa_id: str
    question: str
    score: Union[Literal[0], Literal[1], float]  # 0, 0.5, or 1
    reason: str


class LLMAssessment(BaseModel):
    """Defines the complete, structured JSON object expected from the LLM provider."""

    assessments: list[QAResponseItem]
    overall_summary: str


class TokenUsage(BaseModel):
    """Token usage information for a single LLM request."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    provider: str
    estimated_cost: Optional[Decimal] = None


class CostEstimate(BaseModel):
    """Cost estimation for screening operations."""

    total_papers: int
    estimated_input_tokens_per_paper: int
    estimated_output_tokens_per_paper: int
    estimated_total_tokens: int
    estimated_total_cost: Decimal
    cost_per_input_token: Decimal
    cost_per_output_token: Decimal
    provider: str
    model: str


class UsageReport(BaseModel):
    """Complete usage report for a screening session."""

    session_id: str
    start_time: str
    end_time: Optional[str] = None
    provider: str
    model: str
    total_papers_processed: int
    successful_papers: int
    failed_papers: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost: Decimal
    average_tokens_per_paper: float
    paper_usages: list[TokenUsage] = []


class EvaluationResult(BaseModel):
    """The final, processed result for a single paper."""

    # Paper Details
    id: str
    title: str
    abstract: str

    # Individual Scores & Reasons
    qa1_score: float
    qa1_reason: str
    qa2_score: float
    qa2_reason: str
    qa3_score: float
    qa3_reason: str
    qa4_score: float
    qa4_reason: str

    # Calculated Totals
    total_score: float
    decision: Literal["Include", "Exclude", "Conditional Review"]

    # Metadata
    llm_summary: Optional[str] = None  # Only for LLM evaluations
    error: Optional[str] = None  # To log any processing errors

    # Token usage (only for LLM evaluations)
    token_usage: Optional[TokenUsage] = None


class Conflict(BaseModel):
    """Represents a conflict between two evaluations."""

    id: str
    decision_1: str
    decision_2: str
    total_score_1: float
    total_score_2: float
    score_difference: float


class ConflictReport(BaseModel):
    """The output structure for the compare command."""

    total_papers_compared: int
    total_conflicts: int
    cohen_kappa_score: float
    conflicts: list[Conflict]


class BackupSession(BaseModel):
    """Backup session data for persistent screening."""

    session_id: str
    start_time: str
    provider: str
    model: str
    input_csv_path: str
    output_csv_path: str
    total_papers: int
    processed_papers: list[EvaluationResult] = []
    failed_papers: list[EvaluationResult] = []  # Track failed papers separately
    processed_paper_ids: list[
        str
    ] = []  # Changed from set to list for JSON serialization
    usage_tracker_data: Optional[dict] = None
    last_updated: str

    def model_post_init(self, __context) -> None:
        """Update processed_paper_ids after model initialization."""
        # Convert list back to set for operations, but keep list for serialization
        if isinstance(self.processed_paper_ids, list):
            self._processed_paper_ids_set = set(self.processed_paper_ids)
        else:
            self._processed_paper_ids_set = set()
            self.processed_paper_ids = []

        # Update from processed_papers if needed
        for eval_result in self.processed_papers:
            if eval_result.id not in self._processed_paper_ids_set:
                self._processed_paper_ids_set.add(eval_result.id)
                self.processed_paper_ids.append(eval_result.id)

    def add_processed_paper(self, evaluation: EvaluationResult) -> None:
        """Add a processed paper to the backup."""
        if not hasattr(self, "_processed_paper_ids_set"):
            self._processed_paper_ids_set = set(self.processed_paper_ids)

        if evaluation.id not in self._processed_paper_ids_set:
            self.processed_papers.append(evaluation)
            self._processed_paper_ids_set.add(evaluation.id)
            self.processed_paper_ids.append(evaluation.id)
            self.last_updated = datetime.now().isoformat()

    def add_failed_paper(self, evaluation: EvaluationResult) -> None:
        """Add a failed paper to the backup (for tracking but not marking as processed)."""
        self.failed_papers.append(evaluation)
        self.last_updated = datetime.now().isoformat()

    def is_paper_processed(self, paper_id: str) -> bool:
        """Check if a paper has already been processed."""
        if not hasattr(self, "_processed_paper_ids_set"):
            self._processed_paper_ids_set = set(self.processed_paper_ids)
        return paper_id in self._processed_paper_ids_set

    def get_remaining_papers(self, all_papers: list) -> list:
        """Get list of papers that haven't been processed yet."""
        return [paper for paper in all_papers if not self.is_paper_processed(paper.id)]
