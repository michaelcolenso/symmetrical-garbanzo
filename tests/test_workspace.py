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
