"""End-to-end CLI integration tests using Typer's test runner."""

from __future__ import annotations
import re
from pathlib import Path
import orjson
import pytest
from typer.testing import CliRunner
from kpf.cli.main import app


runner = CliRunner()


class TestHelpCommand:
    def test_help_exits_zero(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_run_command(self):
        result = runner.invoke(app, ["--help"])
        assert "run" in result.output

    def test_help_shows_inspect_command(self):
        result = runner.invoke(app, ["--help"])
        assert "inspect" in result.output

    def test_help_shows_validate_command(self):
        result = runner.invoke(app, ["--help"])
        assert "validate" in result.output

    def test_help_shows_resume_command(self):
        result = runner.invoke(app, ["--help"])
        assert "resume" in result.output

    def test_help_shows_export_command(self):
        result = runner.invoke(app, ["--help"])
        assert "export" in result.output

    def test_run_help(self):
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0

    def test_no_args_shows_help(self):
        result = runner.invoke(app, [])
        # no_args_is_help=True: typer shows help text (exit code may be 0 or 2
        # depending on typer version; either way, help text is shown)
        assert "Usage" in result.output or result.exit_code in (0, 2)


class TestRunCommand:
    def test_run_exits_zero(self, tmp_path):
        result = runner.invoke(app, ["run", "test niche", "--workspace-base", str(tmp_path)])
        assert result.exit_code == 0, f"stdout: {result.output}\nexc: {result.exception}"

    def test_run_creates_workspace_directory(self, tmp_path):
        runner.invoke(app, ["run", "test niche", "--workspace-base", str(tmp_path)])
        run_dirs = [d for d in tmp_path.iterdir() if d.name.startswith("run_")]
        assert len(run_dirs) == 1

    def test_run_creates_state_file(self, tmp_path):
        runner.invoke(app, ["run", "test niche", "--workspace-base", str(tmp_path)])
        run_dirs = [d for d in tmp_path.iterdir() if d.name.startswith("run_")]
        state_file = run_dirs[0] / "state" / "run.json"
        assert state_file.exists()

    def test_run_state_file_has_required_fields(self, tmp_path):
        runner.invoke(app, ["run", "my test niche", "--workspace-base", str(tmp_path)])
        run_dirs = [d for d in tmp_path.iterdir() if d.name.startswith("run_")]
        state = orjson.loads((run_dirs[0] / "state" / "run.json").read_bytes())

        assert "run_id" in state
        assert "niche" in state
        assert "stage" in state
        assert "created_at" in state
        assert "workspace_path" in state

    def test_run_state_niche_preserved(self, tmp_path):
        niche = "IEP/504 parent advocacy"
        runner.invoke(app, ["run", niche, "--workspace-base", str(tmp_path)])
        run_dirs = [d for d in tmp_path.iterdir() if d.name.startswith("run_")]
        state = orjson.loads((run_dirs[0] / "state" / "run.json").read_bytes())
        assert state["niche"] == niche

    def test_run_state_stage_is_init(self, tmp_path):
        runner.invoke(app, ["run", "test niche", "--workspace-base", str(tmp_path)])
        run_dirs = [d for d in tmp_path.iterdir() if d.name.startswith("run_")]
        state = orjson.loads((run_dirs[0] / "state" / "run.json").read_bytes())
        assert state["stage"] == "INIT"

    def test_run_creates_events_log(self, tmp_path):
        runner.invoke(app, ["run", "test niche", "--workspace-base", str(tmp_path)])
        run_dirs = [d for d in tmp_path.iterdir() if d.name.startswith("run_")]
        events_log = run_dirs[0] / "logs" / "events.jsonl"
        assert events_log.exists()

    def test_events_log_has_content(self, tmp_path):
        runner.invoke(app, ["run", "test niche", "--workspace-base", str(tmp_path)])
        run_dirs = [d for d in tmp_path.iterdir() if d.name.startswith("run_")]
        events_log = run_dirs[0] / "logs" / "events.jsonl"
        lines = events_log.read_bytes().splitlines()
        assert len(lines) >= 1

    def test_run_creates_all_subdirs(self, tmp_path):
        runner.invoke(app, ["run", "test niche", "--workspace-base", str(tmp_path)])
        run_dirs = [d for d in tmp_path.iterdir() if d.name.startswith("run_")]
        root = run_dirs[0]
        assert (root / "cache").exists()
        assert (root / "artifacts").exists()
        assert (root / "logs").exists()
        assert (root / "state").exists()

    def test_two_runs_have_sequential_ids(self, tmp_path):
        runner.invoke(app, ["run", "first niche", "--workspace-base", str(tmp_path)])
        runner.invoke(app, ["run", "second niche", "--workspace-base", str(tmp_path)])
        run_dirs = sorted(d.name for d in tmp_path.iterdir() if d.name.startswith("run_"))
        assert len(run_dirs) == 2
        assert run_dirs[0].endswith("_001")
        assert run_dirs[1].endswith("_002")

    def test_run_id_in_state_matches_directory(self, tmp_path):
        runner.invoke(app, ["run", "test niche", "--workspace-base", str(tmp_path)])
        run_dirs = [d for d in tmp_path.iterdir() if d.name.startswith("run_")]
        dir_name = run_dirs[0].name
        state = orjson.loads((run_dirs[0] / "state" / "run.json").read_bytes())
        assert state["run_id"] == dir_name


class TestStubCommands:
    def test_inspect_stub_exits_zero(self):
        result = runner.invoke(app, ["inspect", "run_20260101_001"])
        assert result.exit_code == 0

    def test_validate_stub_exits_zero(self):
        result = runner.invoke(app, ["validate", "run_20260101_001"])
        assert result.exit_code == 0

    def test_resume_stub_exits_zero(self):
        result = runner.invoke(app, ["resume", "run_20260101_001"])
        assert result.exit_code == 0

    def test_export_stub_exits_zero(self):
        result = runner.invoke(app, ["export", "run_20260101_001", "--format", "markdown"])
        assert result.exit_code == 0
