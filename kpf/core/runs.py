from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import orjson

from kpf.config.settings import Settings
from kpf.core.clock import utc_timestamp
from kpf.core.logging import log_event


@dataclass(frozen=True)
class RunPaths:
    root: Path
    config_file: Path
    run_log_file: Path
    run_state_file: Path
    artifacts_dir: Path


class RunManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def paths_for(self, run_id: str) -> RunPaths:
        root = self.settings.workspace_root / run_id
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(f"Run not found: {run_id}")

        return RunPaths(
            root=root,
            config_file=root / "config.json",
            run_log_file=root / "logs" / "run.jsonl",
            run_state_file=root / "state" / "run_state.json",
            artifacts_dir=root / "artifacts",
        )

    def read_state(self, run_id: str) -> dict[str, Any]:
        paths = self.paths_for(run_id)
        if not paths.run_state_file.exists():
            raise FileNotFoundError(f"Missing run state file: {paths.run_state_file}")
        return orjson.loads(paths.run_state_file.read_bytes())

    def write_state(self, run_id: str, state: dict[str, Any]) -> None:
        paths = self.paths_for(run_id)
        paths.run_state_file.write_bytes(orjson.dumps(state, option=orjson.OPT_INDENT_2))

    def read_events(self, run_id: str) -> list[dict[str, Any]]:
        paths = self.paths_for(run_id)
        if not paths.run_log_file.exists():
            return []

        events: list[dict[str, Any]] = []
        with paths.run_log_file.open("rb") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                events.append(orjson.loads(line))
        return events

    def resume(self, run_id: str) -> dict[str, Any]:
        state = self.read_state(run_id)
        state["status"] = "running"
        state["updated_at"] = utc_timestamp()
        self.write_state(run_id, state)
        paths = self.paths_for(run_id)
        log_event(paths.run_log_file, "run.resumed", {"run_id": run_id})
        return state

    def export_markdown(self, run_id: str) -> Path:
        paths = self.paths_for(run_id)
        state = self.read_state(run_id)
        events = self.read_events(run_id)
        paths.artifacts_dir.mkdir(parents=True, exist_ok=True)
        export_path = paths.artifacts_dir / "summary.md"

        lines = [
            f"# KPF Run Summary: {run_id}",
            "",
            "## Objective",
            state.get("objective", "(unknown)"),
            "",
            "## Status",
            f"- Stage: `{state.get('stage', 'UNKNOWN')}`",
            f"- Status: `{state.get('status', 'unknown')}`",
            f"- Created at: `{state.get('created_at', 'unknown')}`",
            f"- Updated at: `{state.get('updated_at', 'n/a')}`",
            "",
            "## Event Log",
        ]

        if events:
            lines.append("| Timestamp | Event | Payload |")
            lines.append("|---|---|---|")
            for event in events:
                lines.append(
                    f"| {event.get('ts', '')} | {event.get('event', '')} | `{event.get('payload', {})}` |"
                )
        else:
            lines.append("No events recorded.")

        lines.append("")
        export_path.write_text("\n".join(lines), encoding="utf-8")
        return export_path
