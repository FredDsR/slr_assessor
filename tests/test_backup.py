"""Tests for the backup utility module."""

import json
import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, Mock
from slr_assessor.utils.backup import BackupManager
from slr_assessor.models import BackupSession, EvaluationResult, Paper


class TestBackupManager:
    """Test the BackupManager class."""

    def test_init(self):
        """Test BackupManager initialization."""
        backup_path = "/tmp/test_backup.json"
        manager = BackupManager(backup_path)

        assert manager.backup_file_path == Path(backup_path)
        assert manager.session is None

    def test_load_or_create_session_new(self):
        """Test creating a new session when no backup exists."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            backup_path = temp_file.name

        # Delete the file to simulate no existing backup
        os.unlink(backup_path)

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            assert isinstance(session, BackupSession)
            assert session.provider == "openai"
            assert session.model == "gpt-4"
            assert session.total_papers == 100
            assert len(session.processed_papers) == 0
            assert session.session_id is not None
        finally:
            if Path(backup_path).exists():
                os.unlink(backup_path)

    def test_load_or_create_session_existing_compatible(self):
        """Test loading existing compatible session."""
        # Create a temporary backup file with compatible session
        existing_session = BackupSession(
            session_id="test-session-id",
            start_time="2025-01-01T10:00:00",
            provider="openai",
            model="gpt-4",
            input_csv_path="/tmp/input.csv",
            output_csv_path="/tmp/output.csv",
            total_papers=100,
            last_updated="2025-01-01T10:00:00",
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(existing_session.model_dump(mode="json"), temp_file, indent=2)
            backup_path = temp_file.name

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            assert session.session_id == "test-session-id"
            assert session.provider == "openai"
            assert session.model == "gpt-4"
        finally:
            os.unlink(backup_path)

    def test_load_or_create_session_existing_incompatible(self):
        """Test creating new session when existing backup is incompatible."""
        # Create a temporary backup file with incompatible session
        existing_session = BackupSession(
            session_id="test-session-id",
            start_time="2025-01-01T10:00:00",
            provider="gemini",  # Different provider
            model="gemini-1.5-flash",
            input_csv_path="/tmp/different_input.csv",
            output_csv_path="/tmp/output.csv",
            total_papers=50,
            last_updated="2025-01-01T10:00:00",
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(existing_session.model_dump(mode="json"), temp_file, indent=2)
            backup_path = temp_file.name

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            # Should create new session due to incompatibility
            assert session.session_id != "test-session-id"
            assert session.provider == "openai"
            assert session.model == "gpt-4"
        finally:
            os.unlink(backup_path)

    def test_load_or_create_session_corrupted_backup(self):
        """Test creating new session when backup file is corrupted."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write("invalid json content")
            backup_path = temp_file.name

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            # Should create new session due to corruption
            assert isinstance(session, BackupSession)
            assert session.provider == "openai"
        finally:
            os.unlink(backup_path)

    def test_add_processed_paper(self, sample_evaluation_result):
        """Test adding a processed paper."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            backup_path = temp_file.name

        os.unlink(backup_path)  # Delete to start fresh

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            manager.add_processed_paper(sample_evaluation_result)

            assert len(session.processed_papers) == 1
            assert session.processed_papers[0].id == "paper_001"
            assert session.is_paper_processed("paper_001")

            # Check that backup file was created
            assert Path(backup_path).exists()
        finally:
            if Path(backup_path).exists():
                os.unlink(backup_path)

    def test_add_processed_paper_no_session(self, sample_evaluation_result):
        """Test adding processed paper without active session raises error."""
        manager = BackupManager("/tmp/test.json")

        with pytest.raises(RuntimeError, match="No active backup session"):
            manager.add_processed_paper(sample_evaluation_result)

    def test_add_failed_paper(self, sample_evaluation_result):
        """Test adding a failed paper."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            backup_path = temp_file.name

        os.unlink(backup_path)

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            manager.add_failed_paper(sample_evaluation_result)

            assert len(session.failed_papers) == 1
            assert session.failed_papers[0].id == "paper_001"
            # Failed papers are not marked as processed
            assert not session.is_paper_processed("paper_001")
        finally:
            if Path(backup_path).exists():
                os.unlink(backup_path)

    def test_save_backup(self):
        """Test saving backup to file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            backup_path = temp_file.name

        os.unlink(backup_path)

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            manager.save_backup()

            assert Path(backup_path).exists()

            # Verify file content
            with open(backup_path) as f:
                data = json.load(f)
                assert data["provider"] == "openai"
                assert data["model"] == "gpt-4"
                assert data["total_papers"] == 100
        finally:
            if Path(backup_path).exists():
                os.unlink(backup_path)

    def test_save_backup_no_session(self):
        """Test saving backup without active session raises error."""
        manager = BackupManager("/tmp/test.json")

        with pytest.raises(RuntimeError, match="No active backup session"):
            manager.save_backup()

    def test_get_remaining_papers(self, sample_papers, sample_evaluation_result):
        """Test getting remaining unprocessed papers."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            backup_path = temp_file.name

        os.unlink(backup_path)

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=3,
            )

            # Add one processed paper
            manager.add_processed_paper(sample_evaluation_result)

            remaining = manager.get_remaining_papers(sample_papers)

            assert len(remaining) == 2
            remaining_ids = [paper.id for paper in remaining]
            assert "paper_001" not in remaining_ids
            assert "paper_002" in remaining_ids
            assert "paper_003" in remaining_ids
        finally:
            if Path(backup_path).exists():
                os.unlink(backup_path)

    def test_get_remaining_papers_no_session(self, sample_papers):
        """Test getting remaining papers without active session."""
        manager = BackupManager("/tmp/test.json")

        remaining = manager.get_remaining_papers(sample_papers)

        # Should return all papers if no session
        assert len(remaining) == len(sample_papers)

    def test_is_paper_processed(self, sample_evaluation_result):
        """Test checking if paper is processed."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            backup_path = temp_file.name

        os.unlink(backup_path)

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            assert not manager.is_paper_processed("paper_001")

            manager.add_processed_paper(sample_evaluation_result)

            assert manager.is_paper_processed("paper_001")
            assert not manager.is_paper_processed("paper_002")
        finally:
            if Path(backup_path).exists():
                os.unlink(backup_path)

    def test_is_paper_processed_no_session(self):
        """Test checking if paper is processed without active session."""
        manager = BackupManager("/tmp/test.json")

        assert not manager.is_paper_processed("paper_001")

    def test_get_processed_papers(self, sample_evaluation_result):
        """Test getting all processed papers."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            backup_path = temp_file.name

        os.unlink(backup_path)

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            processed = manager.get_processed_papers()
            assert len(processed) == 0

            manager.add_processed_paper(sample_evaluation_result)

            processed = manager.get_processed_papers()
            assert len(processed) == 1
            assert processed[0].id == "paper_001"

            # Should return a copy, not the original list
            assert processed is not session.processed_papers
        finally:
            if Path(backup_path).exists():
                os.unlink(backup_path)

    def test_get_processed_papers_no_session(self):
        """Test getting processed papers without active session."""
        manager = BackupManager("/tmp/test.json")

        processed = manager.get_processed_papers()
        assert len(processed) == 0

    def test_update_usage_tracker_data(self):
        """Test updating usage tracker data."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            backup_path = temp_file.name

        os.unlink(backup_path)

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            tracker_data = {"total_tokens": 1500, "total_cost": 0.45}
            manager.update_usage_tracker_data(tracker_data)

            assert session.usage_tracker_data == tracker_data

            # Verify last_updated was changed
            assert session.last_updated != session.start_time
        finally:
            if Path(backup_path).exists():
                os.unlink(backup_path)

    def test_update_usage_tracker_data_no_session(self):
        """Test updating usage tracker data without active session."""
        manager = BackupManager("/tmp/test.json")

        with pytest.raises(RuntimeError, match="No active backup session"):
            manager.update_usage_tracker_data({"test": "data"})

    def test_get_progress_info(self, sample_evaluation_result):
        """Test getting progress information."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            backup_path = temp_file.name

        os.unlink(backup_path)

        try:
            manager = BackupManager(backup_path)
            session = manager.load_or_create_session(
                provider="openai",
                model="gpt-4",
                input_csv_path="/tmp/input.csv",
                output_csv_path="/tmp/output.csv",
                total_papers=100,
            )

            progress = manager.get_progress_info()
            assert progress["processed"] == 0
            assert progress["failed"] == 0
            assert progress["total"] == 100
            assert progress["percentage"] == 0.0
            assert progress["session_id"] == session.session_id

            # Add a processed paper
            manager.add_processed_paper(sample_evaluation_result)

            progress = manager.get_progress_info()
            assert progress["processed"] == 1
            assert progress["percentage"] == 1.0

            # Add a failed paper
            manager.add_failed_paper(sample_evaluation_result)

            progress = manager.get_progress_info()
            assert progress["failed"] == 1
        finally:
            if Path(backup_path).exists():
                os.unlink(backup_path)

    def test_get_progress_info_no_session(self):
        """Test getting progress information without active session."""
        manager = BackupManager("/tmp/test.json")

        progress = manager.get_progress_info()
        assert progress["processed"] == 0
        assert progress["total"] == 0
        assert progress["failed"] == 0
        assert progress["percentage"] == 0.0

    @patch('slr_assessor.utils.backup.Path.mkdir')
    def test_save_backup_creates_directory(self, mock_mkdir):
        """Test that save_backup creates parent directory if needed."""
        backup_path = "/nonexistent/directory/backup.json"
        manager = BackupManager(backup_path)
        manager.session = BackupSession(
            session_id="test",
            start_time="2025-01-01T10:00:00",
            provider="openai",
            model="gpt-4",
            input_csv_path="/tmp/input.csv",
            output_csv_path="/tmp/output.csv",
            total_papers=100,
            last_updated="2025-01-01T10:00:00",
        )

        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value = Mock()
            manager.save_backup()

            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
