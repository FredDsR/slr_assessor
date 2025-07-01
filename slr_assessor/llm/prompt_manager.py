"""Prompt versioning and management system."""

import hashlib
import json
from typing import Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel


class PromptVersion(BaseModel):
    """Represents a specific version of assessment prompts."""

    version: str
    name: str
    description: str
    qa_questions: Dict[str, str]
    template: str
    created_date: str
    is_active: bool = True


class PromptManager:
    """Manages different versions of assessment prompts."""

    def __init__(self, custom_prompts_dir: Optional[Path] = None):
        self.custom_prompts_dir = custom_prompts_dir
        self._versions: Dict[str, PromptVersion] = {}
        self._load_built_in_versions()
        if custom_prompts_dir:
            self._load_custom_versions()

    def _load_built_in_versions(self):
        """Load built-in prompt versions from the prompts package."""
        try:
            from .prompts import BUILT_IN_PROMPTS
            self._versions.update(BUILT_IN_PROMPTS)
        except ImportError as e:
            print(f"Warning: Could not load built-in prompts: {e}")

    def _load_custom_versions(self):
        """Load custom prompt versions from user files."""
        if not self.custom_prompts_dir or not self.custom_prompts_dir.exists():
            return

        for version_file in self.custom_prompts_dir.glob("*.json"):
            try:
                with open(version_file) as f:
                    version_data = json.load(f)
                    version = PromptVersion(**version_data)
                    self._versions[version.version] = version
                    print(f"Loaded custom prompt version: {version.version}")
            except Exception as e:
                print(f"Warning: Could not load custom prompt from {version_file}: {e}")

    def get_version(self, version: str) -> PromptVersion:
        """Get a specific prompt version."""
        if version not in self._versions:
            available = list(self._versions.keys())
            raise ValueError(f"Prompt version '{version}' not found. Available: {available}")
        return self._versions[version]

    def list_versions(self) -> List[PromptVersion]:
        """List all available prompt versions."""
        return list(self._versions.values())

    def get_built_in_versions(self) -> List[PromptVersion]:
        """Get only built-in prompt versions."""
        try:
            from .prompts import BUILT_IN_PROMPTS
            return list(BUILT_IN_PROMPTS.values())
        except ImportError:
            return []

    def get_custom_versions(self) -> List[PromptVersion]:
        """Get only custom prompt versions."""
        built_in_keys = set()
        try:
            from .prompts import BUILT_IN_PROMPTS
            built_in_keys = set(BUILT_IN_PROMPTS.keys())
        except ImportError:
            pass

        return [v for k, v in self._versions.items() if k not in built_in_keys]

    def format_prompt(self, version: str, abstract_text: str) -> str:
        """Format assessment prompt with given version and abstract."""
        prompt_version = self.get_version(version)
        return prompt_version.template.format(
            abstract_text=abstract_text,
            qa1_question=prompt_version.qa_questions["QA1"],
            qa2_question=prompt_version.qa_questions["QA2"],
            qa3_question=prompt_version.qa_questions["QA3"],
            qa4_question=prompt_version.qa_questions["QA4"],
        )

    def get_prompt_hash(self, version: str) -> str:
        """Get a hash of the prompt for exact identification."""
        prompt_version = self.get_version(version)
        content = json.dumps({
            "template": prompt_version.template,
            "qa_questions": prompt_version.qa_questions
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def create_custom_version(self, version: str, name: str, description: str,
                             qa_questions: Dict[str, str], template: str,
                             save_to_file: bool = True) -> PromptVersion:
        """Create a new custom prompt version."""
        if version in self._versions:
            raise ValueError(f"Version '{version}' already exists")

        new_version = PromptVersion(
            version=version,
            name=name,
            description=description,
            qa_questions=qa_questions,
            template=template,
            created_date="2025-07-01",
            is_active=True
        )

        self._versions[version] = new_version

        # Save to file if requested and custom directory is set
        if save_to_file and self.custom_prompts_dir:
            self.custom_prompts_dir.mkdir(parents=True, exist_ok=True)
            version_file = self.custom_prompts_dir / f"{version}.json"
            with open(version_file, 'w') as f:
                json.dump(new_version.model_dump(), f, indent=2)

        return new_version
