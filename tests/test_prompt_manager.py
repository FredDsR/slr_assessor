"""Tests for the prompt versioning system."""

import json
import tempfile
from pathlib import Path

import pytest

from slr_assessor.llm.prompt_manager import PromptManager, PromptVersion


def test_prompt_manager_load_built_in_versions():
    """Test loading built-in prompt versions."""
    manager = PromptManager()
    versions = manager.list_versions()

    assert len(versions) >= 3  # v1.0, v1.1, v2.0
    version_keys = [v.version for v in versions]
    assert "v1.0" in version_keys
    assert "v1.1" in version_keys
    assert "v2.0" in version_keys


def test_prompt_manager_get_version():
    """Test getting a specific prompt version."""
    manager = PromptManager()

    # Test valid version
    v1_0 = manager.get_version("v1.0")
    assert v1_0.version == "v1.0"
    assert v1_0.name == "Default SLR Assessment"
    assert "QA1" in v1_0.qa_questions
    assert "{abstract_text}" in v1_0.template

    # Test invalid version
    with pytest.raises(ValueError, match="Prompt version 'invalid' not found"):
        manager.get_version("invalid")


def test_prompt_manager_format_prompt():
    """Test formatting a prompt with abstract text."""
    manager = PromptManager()
    abstract = "This is a test abstract about AI and traditional communities."

    formatted = manager.format_prompt("v1.0", abstract)

    assert abstract in formatted
    assert "{abstract_text}" not in formatted
    assert "{qa1_question}" not in formatted
    assert "Does the abstract clearly present" in formatted


def test_prompt_manager_get_prompt_hash():
    """Test getting a hash for a prompt version."""
    manager = PromptManager()

    hash1 = manager.get_prompt_hash("v1.0")
    hash2 = manager.get_prompt_hash("v1.0")
    hash3 = manager.get_prompt_hash("v1.1")

    # Same version should produce same hash
    assert hash1 == hash2

    # Different versions should produce different hashes
    assert hash1 != hash3

    # Hash should be 16 characters
    assert len(hash1) == 16


def test_prompt_manager_get_built_in_versions():
    """Test getting only built-in versions."""
    manager = PromptManager()
    built_in = manager.get_built_in_versions()

    assert len(built_in) >= 3
    versions = [v.version for v in built_in]
    assert "v1.0" in versions
    assert "v1.1" in versions
    assert "v2.0" in versions


def test_prompt_manager_custom_versions():
    """Test creating and loading custom prompt versions."""
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_dir = Path(temp_dir)

        # Create a custom prompt version file
        custom_version = {
            "version": "v1.5",
            "name": "Test Custom Prompt",
            "description": "A test custom prompt version",
            "qa_questions": {
                "QA1": "Test question 1?",
                "QA2": "Test question 2?",
                "QA3": "Test question 3?",
                "QA4": "Test question 4?",
            },
            "template": "Test template: {abstract_text}",
            "created_date": "2025-07-01",
            "is_active": True
        }

        custom_file = custom_dir / "v1.5.json"
        with open(custom_file, 'w') as f:
            json.dump(custom_version, f)

        # Create manager with custom directory
        manager = PromptManager(custom_prompts_dir=custom_dir)

        # Should have both built-in and custom versions
        all_versions = manager.list_versions()
        version_keys = [v.version for v in all_versions]
        assert "v1.0" in version_keys  # Built-in
        assert "v1.5" in version_keys  # Custom

        # Test getting custom version
        custom = manager.get_version("v1.5")
        assert custom.name == "Test Custom Prompt"

        # Test custom versions method
        custom_versions = manager.get_custom_versions()
        custom_keys = [v.version for v in custom_versions]
        assert "v1.5" in custom_keys
        assert "v1.0" not in custom_keys  # Built-in should not be in custom list


def test_prompt_manager_create_custom_version():
    """Test creating a new custom prompt version."""
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_dir = Path(temp_dir)
        manager = PromptManager(custom_prompts_dir=custom_dir)

        qa_questions = {
            "QA1": "New question 1?",
            "QA2": "New question 2?",
            "QA3": "New question 3?",
            "QA4": "New question 4?",
        }

        template = "New template: {abstract_text} with {qa1_question}"

        # Create new version
        new_version = manager.create_custom_version(
            version="v3.0",
            name="New Test Version",
            description="A newly created test version",
            qa_questions=qa_questions,
            template=template
        )

        assert new_version.version == "v3.0"
        assert new_version.name == "New Test Version"

        # Should be available through manager
        retrieved = manager.get_version("v3.0")
        assert retrieved.version == "v3.0"

        # Should be saved to file
        version_file = custom_dir / "v3.0.json"
        assert version_file.exists()


def test_prompt_manager_create_duplicate_version():
    """Test that creating a duplicate version raises an error."""
    manager = PromptManager()

    with pytest.raises(ValueError, match="Version 'v1.0' already exists"):
        manager.create_custom_version(
            version="v1.0",  # This already exists
            name="Duplicate",
            description="This should fail",
            qa_questions={"QA1": "test"},
            template="test"
        )


def test_prompt_version_model():
    """Test the PromptVersion model directly."""
    version = PromptVersion(
        version="test",
        name="Test Version",
        description="A test version",
        qa_questions={"QA1": "Test?"},
        template="Test: {abstract_text}",
        created_date="2025-07-01",
        is_active=True
    )

    assert version.version == "test"
    assert version.is_active is True
    assert "QA1" in version.qa_questions
