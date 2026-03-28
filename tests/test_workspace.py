from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from kpf.cli.main import app


runner = CliRunner()


def test_kpf_help_smoke() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "KPF" in result.output


def test_run_creates_workspace_and_initial_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["run", "test niche"])

    assert result.exit_code == 0
    workspaces = tmp_path / "workspaces"
    created = [p for p in workspaces.iterdir() if p.is_dir()]
    assert len(created) == 1

    run_root = created[0]
    run_state = run_root / "state" / "run_state.json"
    run_log = run_root / "logs" / "run.jsonl"

    assert run_state.exists()
    assert run_log.exists()

    state_data = json.loads(run_state.read_text(encoding="utf-8"))
    assert state_data["stage"] == "INIT"
    assert state_data["objective"] == "test niche"


def test_inspect_validate_resume_and_export(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    run_result = runner.invoke(app, ["run", "small business taxes"])
    assert run_result.exit_code == 0

    run_root = next((tmp_path / "workspaces").iterdir())
    run_id = run_root.name

    inspect_result = runner.invoke(app, ["inspect", run_id])
    assert inspect_result.exit_code == 0
    assert "Objective:" in inspect_result.output

    validate_result = runner.invoke(app, ["validate", run_id])
    assert validate_result.exit_code == 0
    assert "Validation passed" in validate_result.output

    resume_result = runner.invoke(app, ["resume", run_id])
    assert resume_result.exit_code == 0
    assert "Run resumed" in resume_result.output

    export_result = runner.invoke(app, ["export", run_id, "--format", "markdown"])
    assert export_result.exit_code == 0

    summary = run_root / "artifacts" / "summary.md"
    assert summary.exists()
    assert "KPF Run Summary" in summary.read_text(encoding="utf-8")
