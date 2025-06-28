"""SLR Assessor CLI - A tool for systematic literature review paper screening."""

__version__ = "2.0.0"
__author__ = "SLR Assessor Team"

from .cli import app
from .models import ConflictReport, EvaluationResult, Paper

__all__ = ["Paper", "EvaluationResult", "ConflictReport", "app"]
