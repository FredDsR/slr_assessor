"""SLR Assessor CLI - A tool for systematic literature review paper screening."""

__version__ = "2.0.0"
__author__ = "SLR Assessor Team"

from .models import Paper, EvaluationResult, ConflictReport
from .cli import app

__all__ = ["Paper", "EvaluationResult", "ConflictReport", "app"]
