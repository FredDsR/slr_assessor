"""Tests for the LLM prompt module."""

import pytest
from slr_assessor.llm.prompt import (
    QA_QUESTIONS,
    ASSESSMENT_PROMPT_TEMPLATE,
    format_assessment_prompt,
)


def test_qa_questions_structure():
    """Test that QA questions are properly defined."""
    assert isinstance(QA_QUESTIONS, dict)
    assert len(QA_QUESTIONS) == 4
    assert "QA1" in QA_QUESTIONS
    assert "QA2" in QA_QUESTIONS
    assert "QA3" in QA_QUESTIONS
    assert "QA4" in QA_QUESTIONS


def test_qa_questions_content():
    """Test that QA questions contain expected content."""
    assert "objective" in QA_QUESTIONS["QA1"].lower()
    assert "practical application" in QA_QUESTIONS["QA2"].lower()
    assert "traditional community" in QA_QUESTIONS["QA3"].lower()
    assert "integration" in QA_QUESTIONS["QA4"].lower()
    assert "ai" in QA_QUESTIONS["QA4"].lower()


def test_qa_questions_are_strings():
    """Test that all QA questions are strings."""
    for qa_id, question in QA_QUESTIONS.items():
        assert isinstance(question, str)
        assert len(question) > 0


def test_assessment_prompt_template_structure():
    """Test that the prompt template has required placeholders."""
    assert "{abstract_text}" in ASSESSMENT_PROMPT_TEMPLATE
    assert "{qa1_question}" in ASSESSMENT_PROMPT_TEMPLATE
    assert "{qa2_question}" in ASSESSMENT_PROMPT_TEMPLATE
    assert "{qa3_question}" in ASSESSMENT_PROMPT_TEMPLATE
    assert "{qa4_question}" in ASSESSMENT_PROMPT_TEMPLATE


def test_assessment_prompt_template_content():
    """Test that prompt template contains expected content."""
    template_lower = ASSESSMENT_PROMPT_TEMPLATE.lower()
    assert "academic researcher" in template_lower
    assert "quality assessment" in template_lower
    assert "json" in template_lower
    assert "assessments" in template_lower
    assert "overall_summary" in template_lower


def test_assessment_prompt_template_json_structure():
    """Test that prompt template describes proper JSON structure."""
    assert '"assessments"' in ASSESSMENT_PROMPT_TEMPLATE
    assert '"qa_id"' in ASSESSMENT_PROMPT_TEMPLATE
    assert '"question"' in ASSESSMENT_PROMPT_TEMPLATE
    assert '"score"' in ASSESSMENT_PROMPT_TEMPLATE
    assert '"reason"' in ASSESSMENT_PROMPT_TEMPLATE
    assert '"overall_summary"' in ASSESSMENT_PROMPT_TEMPLATE


def test_assessment_prompt_template_scoring_instructions():
    """Test that prompt template includes scoring instructions."""
    assert "0, 0.5, or 1" in ASSESSMENT_PROMPT_TEMPLATE or "0.5" in ASSESSMENT_PROMPT_TEMPLATE
    assert "satisfies" in ASSESSMENT_PROMPT_TEMPLATE.lower()


def test_format_assessment_prompt_basic():
    """Test basic prompt formatting with sample abstract."""
    abstract = "This is a sample abstract for testing purposes."

    formatted_prompt = format_assessment_prompt(abstract)

    assert isinstance(formatted_prompt, str)
    assert abstract in formatted_prompt
    assert len(formatted_prompt) > len(ASSESSMENT_PROMPT_TEMPLATE)


def test_format_assessment_prompt_all_placeholders_replaced():
    """Test that all placeholders are replaced in formatted prompt."""
    abstract = "Sample abstract text."

    formatted_prompt = format_assessment_prompt(abstract)

    # Check that original placeholders are not present
    assert "{abstract_text}" not in formatted_prompt
    assert "{qa1_question}" not in formatted_prompt
    assert "{qa2_question}" not in formatted_prompt
    assert "{qa3_question}" not in formatted_prompt
    assert "{qa4_question}" not in formatted_prompt


def test_format_assessment_prompt_qa_questions_included():
    """Test that all QA questions are included in formatted prompt."""
    abstract = "Sample abstract text."

    formatted_prompt = format_assessment_prompt(abstract)

    for question in QA_QUESTIONS.values():
        assert question in formatted_prompt


def test_format_assessment_prompt_special_characters():
    """Test formatting with special characters in abstract."""
    abstract = 'Abstract with "quotes", newlines\n, and symbols @#$%.'

    formatted_prompt = format_assessment_prompt(abstract)

    assert abstract in formatted_prompt
    assert '"quotes"' in formatted_prompt
    assert '\n' in formatted_prompt
    assert '@#$%' in formatted_prompt


def test_format_assessment_prompt_empty_abstract():
    """Test formatting with empty abstract."""
    abstract = ""

    formatted_prompt = format_assessment_prompt(abstract)

    assert isinstance(formatted_prompt, str)
    assert len(formatted_prompt) > 0
    # All QA questions should still be present
    for question in QA_QUESTIONS.values():
        assert question in formatted_prompt


def test_format_assessment_prompt_long_abstract():
    """Test formatting with very long abstract."""
    abstract = "This is a very long abstract. " * 100

    formatted_prompt = format_assessment_prompt(abstract)

    assert abstract in formatted_prompt
    assert len(formatted_prompt) > len(abstract)


def test_format_assessment_prompt_unicode():
    """Test formatting with unicode characters in abstract."""
    abstract = "Abstract with unicode: café, naïve, résumé, 中文, العربية"

    formatted_prompt = format_assessment_prompt(abstract)

    assert abstract in formatted_prompt
    assert "café" in formatted_prompt
    assert "中文" in formatted_prompt
    assert "العربية" in formatted_prompt


def test_format_assessment_prompt_structure():
    """Test that formatted prompt maintains expected structure."""
    abstract = "Sample abstract for structure testing."

    formatted_prompt = format_assessment_prompt(abstract)

    # Should contain JSON structure elements
    assert "assessments" in formatted_prompt
    assert "qa_id" in formatted_prompt
    assert "QA1" in formatted_prompt
    assert "QA2" in formatted_prompt
    assert "QA3" in formatted_prompt
    assert "QA4" in formatted_prompt
    assert "overall_summary" in formatted_prompt


def test_format_assessment_prompt_consistent():
    """Test that same abstract produces same formatted prompt."""
    abstract = "Consistent testing abstract."

    prompt1 = format_assessment_prompt(abstract)
    prompt2 = format_assessment_prompt(abstract)

    assert prompt1 == prompt2
