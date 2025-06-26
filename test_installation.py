#!/usr/bin/env python3
"""
Test script to verify SLR Assessor installation and basic functionality.
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from slr_assessor.models import Paper, EvaluationResult, ConflictReport  # noqa
        from slr_assessor.core.evaluator import (
            calculate_decision,
            create_evaluation_result,
        )  # noqa
        from slr_assessor.core.comparator import compare_evaluations  # noqa
        from slr_assessor.llm.prompt import format_assessment_prompt  # noqa
        from slr_assessor.utils.io import read_papers_from_csv  # noqa

        print("✅ All core modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    return True


def test_models():
    """Test Pydantic models."""
    print("Testing models...")

    try:
        from slr_assessor.models import Paper, EvaluationResult

        # Test Paper model
        paper = Paper(
            id="test1", title="Test Paper", abstract="This is a test abstract."
        )

        # Test EvaluationResult model
        eval_result = EvaluationResult(
            id="test1",
            title="Test Paper",
            abstract="This is a test abstract.",
            qa1_score=1.0,
            qa1_reason="Good objective",
            qa2_score=0.5,
            qa2_reason="Partial application",
            qa3_score=0.0,
            qa3_reason="No context",
            qa4_score=1.0,
            qa4_reason="Good integration",
            total_score=2.5,
            decision="Include",
        )

        print("✅ Models work correctly")
        return True

    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False


def test_evaluator():
    """Test evaluation logic."""
    print("Testing evaluator...")

    try:
        from slr_assessor.core.evaluator import (
            calculate_decision,
            create_evaluation_result,
        )

        # Test decision calculation
        assert calculate_decision(3.0) == "Include"
        assert calculate_decision(2.0) == "Conditional Review"
        assert calculate_decision(1.0) == "Exclude"

        # Test evaluation result creation
        qa_scores = {"qa1": 1.0, "qa2": 0.5, "qa3": 0.0, "qa4": 1.0}
        qa_reasons = {"qa1": "Good", "qa2": "OK", "qa3": "Poor", "qa4": "Good"}

        result = create_evaluation_result(
            paper_id="test1",
            title="Test",
            abstract="Test abstract",
            qa_scores=qa_scores,
            qa_reasons=qa_reasons,
        )

        assert result.total_score == 2.5
        assert result.decision == "Include"

        print("✅ Evaluator works correctly")
        return True

    except Exception as e:
        print(f"❌ Evaluator test failed: {e}")
        return False


def test_prompt():
    """Test prompt formatting."""
    print("Testing prompt formatting...")

    try:
        from slr_assessor.llm.prompt import format_assessment_prompt

        prompt = format_assessment_prompt(
            "This is a test abstract about AI and traditional medicine."
        )

        assert "This is a test abstract about AI and traditional medicine." in prompt
        assert "QA1" in prompt
        assert "JSON" in prompt

        print("✅ Prompt formatting works correctly")
        return True

    except Exception as e:
        print(f"❌ Prompt test failed: {e}")
        return False


def test_io():
    """Test I/O functions with sample data."""
    print("Testing I/O functions...")

    try:
        from slr_assessor.utils.io import read_papers_from_csv

        # Test with sample file if it exists
        sample_file = Path("examples/sample_papers.csv")
        if sample_file.exists():
            papers = read_papers_from_csv(str(sample_file))
            assert len(papers) > 0
            assert papers[0].id
            assert papers[0].title
            assert papers[0].abstract
            print(f"✅ Successfully read {len(papers)} papers from sample file")
        else:
            print("⚠️  Sample file not found, skipping I/O test")

        return True

    except Exception as e:
        print(f"❌ I/O test failed: {e}")
        return False


def test_cli_help():
    """Test that CLI help works."""
    print("Testing CLI...")

    try:
        import subprocess

        result = subprocess.run(
            ["uv", "run", "slr-assessor", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0 and "slr-assessor" in result.stdout:
            print("✅ CLI help works correctly")
            return True
        else:
            print(f"❌ CLI test failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Running SLR Assessor tests...\n")

    tests = [
        test_imports,
        test_models,
        test_evaluator,
        test_prompt,
        test_io,
        test_cli_help,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()

    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! SLR Assessor is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the installation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
