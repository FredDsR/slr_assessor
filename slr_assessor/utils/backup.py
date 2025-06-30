"""Backup utilities for persistent screening sessions."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models import BackupSession, EvaluationResult, Paper


class BackupManager:
    """Manages backup operations for screening sessions."""

    def __init__(self, backup_file_path: str):
        self.backup_file_path = Path(backup_file_path)
        self.session: Optional[BackupSession] = None

    def load_or_create_session(
        self,
        provider: str,
        model: str,
        input_csv_path: str,
        output_csv_path: str,
        total_papers: int,
    ) -> BackupSession:
        """Load existing backup session or create a new one."""
        if self.backup_file_path.exists():
            try:
                with open(self.backup_file_path, encoding="utf-8") as f:
                    backup_data = json.load(f)
                    self.session = BackupSession(**backup_data)

                    # Validate session compatibility
                    if (
                        self.session.provider != provider
                        or self.session.model != model
                        or self.session.input_csv_path != input_csv_path
                    ):
                        raise ValueError(
                            f"Backup session mismatch: "
                            f"Expected {provider}/{model} with {input_csv_path}, "
                            f"found {self.session.provider}/{self.session.model} "
                            f"with {self.session.input_csv_path}"
                        )

                    print(
                        f"✓ Loaded existing backup session: {len(self.session.processed_papers)} papers already processed"
                    )
                    return self.session

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"⚠ Could not load backup file: {e}")
                print("Creating new backup session...")

        # Create new session
        self.session = BackupSession(
            session_id=str(uuid.uuid4()),
            start_time=datetime.now().isoformat(),
            provider=provider,
            model=model,
            input_csv_path=input_csv_path,
            output_csv_path=output_csv_path,
            total_papers=total_papers,
            last_updated=datetime.now().isoformat(),
        )

        return self.session

    def add_processed_paper(self, evaluation: EvaluationResult) -> None:
        """Add a processed paper and save to backup."""
        if not self.session:
            raise RuntimeError("No active backup session")

        self.session.add_processed_paper(evaluation)
        self.save_backup()

    def add_failed_paper(self, evaluation: EvaluationResult) -> None:
        """Add a failed paper (for tracking but not marking as processed) and save to backup."""
        if not self.session:
            raise RuntimeError("No active backup session")

        self.session.add_failed_paper(evaluation)
        self.save_backup()

    def save_backup(self) -> None:
        """Save current session to backup file."""
        if not self.session:
            raise RuntimeError("No active backup session")

        # Create backup directory if it doesn't exist
        self.backup_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict for JSON serialization
        backup_data = self.session.model_dump(mode="json")

        with open(self.backup_file_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

    def get_remaining_papers(self, all_papers: list[Paper]) -> list[Paper]:
        """Get papers that haven't been processed yet."""
        if not self.session:
            return all_papers

        return self.session.get_remaining_papers(all_papers)

    def is_paper_processed(self, paper_id: str) -> bool:
        """Check if a paper has already been processed."""
        if not self.session:
            return False

        return self.session.is_paper_processed(paper_id)

    def get_processed_papers(self) -> list[EvaluationResult]:
        """Get all processed papers from the session."""
        if not self.session:
            return []

        return self.session.processed_papers.copy()

    def update_usage_tracker_data(self, tracker_data: dict) -> None:
        """Update usage tracker data in the session."""
        if not self.session:
            raise RuntimeError("No active backup session")

        self.session.usage_tracker_data = tracker_data
        self.session.last_updated = datetime.now().isoformat()
        self.save_backup()

    def get_progress_info(self) -> dict:
        """Get current progress information."""
        if not self.session:
            return {"processed": 0, "total": 0, "failed": 0, "percentage": 0.0}

        processed = len(self.session.processed_papers)
        failed = len(self.session.failed_papers)
        total = self.session.total_papers
        percentage = (processed / total * 100) if total > 0 else 0.0

        return {
            "processed": processed,
            "failed": failed,
            "total": total,
            "percentage": percentage,
            "session_id": self.session.session_id,
            "start_time": self.session.start_time,
            "last_updated": self.session.last_updated,
        }
