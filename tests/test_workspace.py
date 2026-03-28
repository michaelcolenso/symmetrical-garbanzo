"""Tests for kpf.core.workspace."""

from __future__ import annotations
import re
from pathlib import Path
import pytest
from kpf.config.settings import Settings
from kpf.core.workspace import WorkspaceManager, WorkspacePaths


@pytest.fixture
def manager(tmp_path: Path) -> WorkspaceManager:
    settings = Settings(workspace_base=tmp_path / "workspaces")
    return WorkspaceManager(settings)


class TestCreateRun:
    def test_creates_root_directory(self, manager):
        paths = manager.create_run()
        assert paths.root.exists()

    def test_creates_all_subdirectories(self, manager):
        paths = manager.create_run()
        assert paths.cache.exists()
        assert paths.artifacts.exists()
        assert paths.logs.exists()
        assert paths.state.exists()
        assert paths.cache_html.exists()
        assert paths.cache_pdf.exists()
        assert paths.cache_screenshots.exists()

    def test_run_id_format(self, manager):
        paths = manager.create_run()
        assert re.match(r"^run_\d{8}_\d{3}$", paths.run_id)

    def test_first_run_is_001(self, manager):
        paths = manager.create_run()
        assert paths.run_id.endswith("_001")

    def test_sequential_numbering(self, manager):
        p1 = manager.create_run()
        p2 = manager.create_run()
        assert p1.run_id.endswith("_001")
        assert p2.run_id.endswith("_002")

    def test_sequential_numbering_three_runs(self, manager):
        p1 = manager.create_run()
        p2 = manager.create_run()
        p3 = manager.create_run()
        assert p1.run_id.endswith("_001")
        assert p2.run_id.endswith("_002")
        assert p3.run_id.endswith("_003")

    def test_date_override_resets_sequence(self, manager):
        p1 = manager.create_run(date_str="20240101")
        p2 = manager.create_run(date_str="20240102")
        assert p1.run_id == "run_20240101_001"
        assert p2.run_id == "run_20240102_001"

    def test_same_date_increments(self, manager):
        p1 = manager.create_run(date_str="20240101")
        p2 = manager.create_run(date_str="20240101")
        assert p1.run_id == "run_20240101_001"
        assert p2.run_id == "run_20240101_002"

    def test_workspace_base_created_if_missing(self, tmp_path):
        base = tmp_path / "does" / "not" / "exist"
        settings = Settings(workspace_base=base)
        manager = WorkspaceManager(settings)
        paths = manager.create_run()
        assert base.exists()
        assert paths.root.exists()

    def test_run_id_matches_directory_name(self, manager):
        paths = manager.create_run()
        assert paths.root.name == paths.run_id

    def test_paths_are_absolute(self, manager):
        paths = manager.create_run()
        assert paths.root.is_absolute()
        assert paths.cache.is_absolute()
        assert paths.artifacts.is_absolute()
        assert paths.logs.is_absolute()
        assert paths.state.is_absolute()


class TestOpenRun:
    def test_open_existing_run(self, manager):
        created = manager.create_run()
        opened = manager.open_run(created.run_id)
        assert opened.run_id == created.run_id
        assert opened.root == created.root

    def test_open_missing_run_raises(self, manager):
        with pytest.raises(FileNotFoundError):
            manager.open_run("run_99991231_001")

    def test_opened_paths_match_created(self, manager):
        created = manager.create_run()
        opened = manager.open_run(created.run_id)
        assert opened.artifacts == created.artifacts
        assert opened.logs == created.logs
        assert opened.state == created.state


class TestListRuns:
    def test_empty_base_returns_empty_list(self, manager):
        assert manager.list_runs() == []

    def test_lists_created_runs(self, manager):
        manager.create_run(date_str="20240101")
        manager.create_run(date_str="20240102")
        runs = manager.list_runs()
        assert len(runs) == 2

    def test_runs_sorted_chronologically(self, manager):
        manager.create_run(date_str="20240103")
        manager.create_run(date_str="20240101")
        manager.create_run(date_str="20240102")
        runs = manager.list_runs()
        assert runs == sorted(runs)


class TestWorkspacePaths:
    def test_run_state_path(self, manager):
        paths = manager.create_run()
        assert paths.run_state_path == paths.state / "run.json"

    def test_events_log_path(self, manager):
        paths = manager.create_run()
        assert paths.events_log_path == paths.logs / "events.jsonl"

    def test_agent_calls_log_path(self, manager):
        paths = manager.create_run()
        assert paths.agent_calls_log_path == paths.logs / "agent_calls.jsonl"

    def test_artifact_helper(self, manager):
        paths = manager.create_run()
        assert paths.artifact("foo.json") == paths.artifacts / "foo.json"

    def test_log_file_helper(self, manager):
        paths = manager.create_run()
        assert paths.log_file("debug.log") == paths.logs / "debug.log"

    def test_state_file_helper(self, manager):
        paths = manager.create_run()
        assert paths.state_file("run.json") == paths.state / "run.json"
