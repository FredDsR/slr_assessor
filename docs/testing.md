# SLR Assessor Test Suite

This document describes the comprehensive unit test suite for the slr_assessor package.

## Overview

The test suite covers all major components of the slr_assessor package:

- **Data Models** (`test_models.py`) - Tests for all Pydantic data models
- **Core Logic** (`test_evaluator.py`, `test_comparator.py`) - Tests for scoring and comparison logic
- **LLM Integration** (`test_prompt.py`, `test_providers.py`) - Tests for prompt formatting and LLM provider abstractions
- **Utilities** (`test_io.py`, `test_cost_calculator.py`, `test_backup.py`, `test_usage_tracker.py`) - Tests for utility functions
- **CLI Interface** (`test_cli.py`) - Basic tests for the command-line interface

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and test configuration
├── test_models.py           # Data model tests
├── test_evaluator.py        # Core evaluation logic tests
├── test_comparator.py       # Evaluation comparison tests
├── test_prompt.py           # LLM prompt formatting tests
├── test_providers.py        # LLM provider integration tests
├── test_io.py               # File I/O utility tests
├── test_cost_calculator.py  # Cost calculation tests
├── test_backup.py           # Backup utility tests
├── test_usage_tracker.py    # Usage tracking tests
└── test_cli.py              # CLI interface tests
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
uv sync --group test
```

### Run All Tests

```bash
# Using pytest directly
uv run pytest tests/ -v

# Using the test runner script
python run_tests.py
```

### Run Specific Test Categories

```bash
# Run only unit tests (exclude integration tests)
python run_tests.py unit

# Run only fast tests (exclude slow tests)
python run_tests.py fast

# Run with coverage report
uv run pytest tests/ --cov=slr_assessor --cov-report=html
```

### Run Individual Test Files

```bash
# Test specific module
uv run pytest tests/test_models.py -v

# Test specific class
uv run pytest tests/test_evaluator.py::TestCalculateDecision -v

# Test specific function
uv run pytest tests/test_evaluator.py::TestCalculateDecision::test_include_decision -v
```

## Test Coverage

The test suite aims for comprehensive coverage of:

- ✅ **Data Models** - All Pydantic models and validation logic
- ✅ **Core Functions** - Evaluation, comparison, and decision logic
- ✅ **LLM Integration** - Prompt formatting and provider abstractions
- ✅ **Utility Functions** - File I/O, cost calculation, backup, and usage tracking
- ✅ **Error Handling** - Invalid inputs, missing files, API failures
- ⚠️ **CLI Interface** - Basic structure testing (full CLI testing requires integration tests)

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `sample_paper` - Single paper for testing
- `sample_papers` - List of papers for testing
- `sample_evaluation_result` - Single evaluation result
- `sample_evaluation_results` - List of evaluation results
- `sample_qa_scores` / `sample_qa_reasons` - QA assessment data
- `sample_token_usage` - Token usage information
- `sample_cost_estimate` - Cost estimation data
- And more...

## Mocking Strategy

The test suite uses `unittest.mock` and `pytest-mock` to:

- Mock external API calls (OpenAI, Gemini, Anthropic)
- Mock file system operations
- Mock expensive operations (token counting, cost calculation)
- Isolate units under test

## Test Markers

Tests can be marked with custom markers:

```python
@pytest.mark.unit
def test_unit_functionality():
    """Unit test - fast, isolated"""
    pass

@pytest.mark.integration
def test_integration_workflow():
    """Integration test - may be slower"""
    pass

@pytest.mark.slow
def test_expensive_operation():
    """Slow test - skip for quick runs"""
    pass

@pytest.mark.network
def test_api_integration():
    """Test requiring network access"""
    pass
```

## Adding New Tests

When adding new functionality:

1. **Create test file** following the `test_*.py` naming convention
2. **Add fixtures** to `conftest.py` if they'll be reused
3. **Use descriptive test names** that explain what is being tested
4. **Test both success and failure cases**
5. **Mock external dependencies** to keep tests isolated
6. **Add docstrings** explaining the test purpose

### Test Structure Example

```python
def test_valid_input():
    """Test that valid input produces expected output."""
    # Arrange
    input_data = create_test_input()

    # Act
    result = new_feature_function(input_data)

    # Assert
    assert result == expected_output


def test_invalid_input_raises_error():
    """Test that invalid input raises appropriate error."""
    with pytest.raises(ValueError, match="expected error message"):
        new_feature_function(invalid_input)


@patch('module.external_dependency')
def test_with_mocked_dependency(mock_dependency):
    """Test behavior with mocked external dependency."""
    mock_dependency.return_value = mock_response

    result = new_feature_function(test_input)

    assert result == expected_result
    mock_dependency.assert_called_once_with(expected_args)
```

## Continuous Integration

The test suite is designed to run in CI/CD environments:

- All tests should be deterministic and not rely on external services
- Use environment variables for configuration when needed
- Mock network calls and file system operations
- Keep test runtime reasonable for CI pipelines

## Troubleshooting

### Common Issues

1. **Import Errors** - Ensure the package is properly installed with `uv sync`
2. **Missing Dependencies** - Install test dependencies with `uv sync --group test`
3. **File Path Issues** - Tests use temporary files and should clean up after themselves
4. **Mock Issues** - Ensure mocks are properly configured and patches are applied to the right modules

### Debug Tips

```bash
# Run with more verbose output
uv run pytest tests/ -vv

# Stop on first failure
uv run pytest tests/ -x

# Show local variables in tracebacks
uv run pytest tests/ --tb=long --showlocals

# Run specific test with print statements
uv run pytest tests/test_models.py::test_valid_paper_creation -s
```

## Contributing

When contributing new tests:

1. Follow the existing test structure and naming conventions
2. Ensure new tests pass and don't break existing ones
3. Add appropriate fixtures for reusable test data
4. Mock external dependencies appropriately
5. Update this documentation if adding new test categories or significant functionality

## Test Design Philosophy

The slr_assessor test suite follows these principles:

- **Function-based testing** - Tests are organized as bare functions rather than classes for simplicity and clarity
- **Descriptive naming** - Test function names clearly describe what is being tested
- **Arrange-Act-Assert** - Tests follow the AAA pattern for clarity
- **Isolation** - Each test is independent and can run in any order
- **Fast execution** - Tests should run quickly to support rapid development
- **Comprehensive coverage** - All code paths and edge cases should be tested
