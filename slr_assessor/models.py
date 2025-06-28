"""Pydantic data models for the SLR Assessor CLI."""

from typing import List, Literal, Optional
from pydantic import BaseModel
from decimal import Decimal


class Paper(BaseModel):
    """Represents a single paper to be screened."""

    id: str
    title: str
    abstract: str


class QAResponseItem(BaseModel):
    """Represents the assessment for a single QA question as returned by the LLM."""

    qa_id: str
    question: str
    score: Literal[0, 0.5, 1]
    reason: str


class LLMAssessment(BaseModel):
    """Defines the complete, structured JSON object expected from the LLM provider."""

    assessments: List[QAResponseItem]
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
    paper_usages: List[TokenUsage] = []


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
    conflicts: List[Conflict]
