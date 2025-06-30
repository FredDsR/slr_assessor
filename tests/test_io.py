"""Tests for the IO utility module."""

import os
import tempfile
from unittest.mock import patch

import pandas as pd
import pytest

from slr_assessor.models import EvaluationResult, Paper
from slr_assessor.utils.io import (
    read_evaluations_from_csv,
    read_human_evaluations_from_csv,
    read_papers_from_csv,
    write_evaluations_to_csv,
)


def test_read_valid_papers_csv():
    """Test reading a valid papers CSV file."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title,abstract\n")
        f.write('paper_001,"Test Paper 1","This is the first test abstract."\n')
        f.write('paper_002,"Test Paper 2","This is the second test abstract."\n')
        temp_file = f.name

    try:
        papers = read_papers_from_csv(temp_file)

        assert len(papers) == 2
        assert isinstance(papers[0], Paper)
        assert papers[0].id == "paper_001"
        assert papers[0].title == "Test Paper 1"
        assert papers[0].abstract == "This is the first test abstract."
        assert papers[1].id == "paper_002"
    finally:
        os.unlink(temp_file)

def test_read_papers_file_not_found():
    """Test reading non-existent CSV file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        read_papers_from_csv("/nonexistent/file.csv")

def test_read_papers_missing_columns():
    """Test reading CSV with missing required columns."""
    # Create CSV with missing columns
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title\n")  # Missing abstract column
        f.write('paper_001,"Test Paper 1"\n')
        temp_file = f.name

    try:
        with pytest.raises(ValueError, match="Missing required columns"):
            read_papers_from_csv(temp_file)
    finally:
        os.unlink(temp_file)

def test_read_papers_empty_csv():
    """Test reading empty CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title,abstract\n")  # Header only
        temp_file = f.name

    try:
        papers = read_papers_from_csv(temp_file)
        assert len(papers) == 0
    finally:
        os.unlink(temp_file)

def test_read_papers_with_special_characters():
    """Test reading papers with special characters."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title,abstract\n")
        f.write('paper_001,"Title with ""quotes""","Abstract with\nnewlines and commas, etc."\n')
        temp_file = f.name

    try:
        papers = read_papers_from_csv(temp_file)
        assert len(papers) == 1
        assert '"quotes"' in papers[0].title
        assert '\n' in papers[0].abstract
    finally:
        os.unlink(temp_file)


def test_read_valid_evaluations_csv():
    """Test reading a valid human evaluations CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title,abstract,qa1_score,qa1_reason,qa2_score,qa2_reason,qa3_score,qa3_reason,qa4_score,qa4_reason\n")
        f.write('paper_001,"Test Paper","Test abstract",1.0,"Good",0.5,"Okay",1.0,"Strong",0.0,"Weak"\n')
        temp_file = f.name

    try:
        evaluations = read_human_evaluations_from_csv(temp_file)

        assert len(evaluations) == 1
        assert isinstance(evaluations[0], EvaluationResult)
        assert evaluations[0].id == "paper_001"
        assert evaluations[0].qa1_score == 1.0
        assert evaluations[0].qa1_reason == "Good"
        assert evaluations[0].total_score == 2.5
        assert evaluations[0].decision == "Include"
    finally:
        os.unlink(temp_file)

def test_read_evaluations_file_not_found():
    """Test reading non-existent evaluations CSV file."""
    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        read_human_evaluations_from_csv("/nonexistent/file.csv")

def test_read_evaluations_missing_columns():
    """Test reading evaluations CSV with missing required columns."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title,abstract,qa1_score\n")  # Missing other columns
        f.write('paper_001,"Test Paper","Test abstract",1.0\n')
        temp_file = f.name

    try:
        with pytest.raises(ValueError, match="Missing required columns"):
            read_human_evaluations_from_csv(temp_file)
    finally:
        os.unlink(temp_file)


def test_read_complete_evaluations_csv():
    """Test reading a complete evaluations CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title,abstract,qa1_score,qa1_reason,qa2_score,qa2_reason,qa3_score,qa3_reason,qa4_score,qa4_reason,total_score,decision,llm_summary\n")
        f.write('paper_001,"Test Paper","Test abstract",1.0,"Good",0.5,"Okay",1.0,"Strong",0.0,"Weak",2.5,"Include","Good paper"\n')
        temp_file = f.name

    try:
        evaluations = read_evaluations_from_csv(temp_file)

        assert len(evaluations) == 1
        assert isinstance(evaluations[0], EvaluationResult)
        assert evaluations[0].id == "paper_001"
        assert evaluations[0].total_score == 2.5
        assert evaluations[0].decision == "Include"
        assert evaluations[0].llm_summary == "Good paper"
    finally:
        os.unlink(temp_file)

def test_read_evaluations_with_optional_columns():
    """Test reading evaluations CSV with some optional columns missing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title,abstract,qa1_score,qa1_reason,qa2_score,qa2_reason,qa3_score,qa3_reason,qa4_score,qa4_reason,total_score,decision\n")
        f.write('paper_001,"Test Paper","Test abstract",1.0,"Good",0.5,"Okay",1.0,"Strong",0.0,"Weak",2.5,"Include"\n')
        temp_file = f.name

    try:
        evaluations = read_evaluations_from_csv(temp_file)

        assert len(evaluations) == 1
        assert evaluations[0].llm_summary is None
        assert evaluations[0].error is None
    finally:
        os.unlink(temp_file)


def test_write_evaluations_to_csv(sample_evaluation_results):
    """Test writing evaluations to CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_file = f.name

    try:
        write_evaluations_to_csv(sample_evaluation_results, temp_file)

        # Read back the file to verify
        df = pd.read_csv(temp_file)

        assert len(df) == 3
        assert "id" in df.columns
        assert "title" in df.columns
        assert "abstract" in df.columns
        assert "qa1_score" in df.columns
        assert "total_score" in df.columns
        assert "decision" in df.columns

        # Check first row data
        assert df.iloc[0]["id"] == "paper_001"
        assert df.iloc[0]["total_score"] == 4.0
        assert df.iloc[0]["decision"] == "Include"
    finally:
        os.unlink(temp_file)

def test_write_empty_evaluations():
    """Test writing empty list of evaluations."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_file = f.name

    try:
        write_evaluations_to_csv([], temp_file)

        # File should exist but be empty (except header)
        df = pd.read_csv(temp_file)
        assert len(df) == 0
    finally:
        os.unlink(temp_file)

def test_write_evaluations_with_optional_fields():
    """Test writing evaluations with optional fields."""
    evaluation = EvaluationResult(
        id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa1_score=1.0,
        qa1_reason="Good",
        qa2_score=0.5,
        qa2_reason="Okay",
        qa3_score=1.0,
        qa3_reason="Strong",
        qa4_score=0.0,
        qa4_reason="Weak",
        total_score=2.5,
        decision="Include",
        llm_summary="Overall good paper",
        error=None,
    )

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_file = f.name

    try:
        write_evaluations_to_csv([evaluation], temp_file)

        df = pd.read_csv(temp_file)
        assert len(df) == 1
        assert df.iloc[0]["llm_summary"] == "Overall good paper"
    finally:
        os.unlink(temp_file)

def test_write_evaluations_with_error():
    """Test writing evaluations with error field."""
    evaluation = EvaluationResult(
        id="paper_001",
        title="Test Paper",
        abstract="Test abstract",
        qa1_score=0.0,
        qa1_reason="",
        qa2_score=0.0,
        qa2_reason="",
        qa3_score=0.0,
        qa3_reason="",
        qa4_score=0.0,
        qa4_reason="",
        total_score=0.0,
        decision="Exclude",
        error="Processing failed",
    )

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_file = f.name

    try:
        write_evaluations_to_csv([evaluation], temp_file)

        df = pd.read_csv(temp_file)
        assert len(df) == 1
        assert df.iloc[0]["error"] == "Processing failed"
    finally:
        os.unlink(temp_file)

def test_write_to_invalid_path(sample_evaluation_results):
    """Test writing to invalid file path."""
    invalid_path = "/nonexistent/directory/file.csv"

    with pytest.raises(Exception):  # Could be FileNotFoundError or PermissionError
        write_evaluations_to_csv(sample_evaluation_results, invalid_path)

@patch('pandas.DataFrame.to_csv')
def test_write_csv_options(mock_to_csv, sample_evaluation_results):
    """Test that CSV is written with correct options."""
    temp_file = "test.csv"

    write_evaluations_to_csv(sample_evaluation_results, temp_file)

    # Verify to_csv was called with expected parameters
    mock_to_csv.assert_called_once_with(temp_file, index=False)
