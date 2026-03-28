from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from kpf.config.settings import Settings
from kpf.core.clock import day_stamp
from kpf.core.ids import short_uuid, slugify


@dataclass(frozen=True)
class WorkspacePaths:
    root: Path
    artifacts: Path
    cache_html: Path
    cache_pdf: Path
    cache_screenshots: Path
    logs: Path
    state: Path

    @property
    def run_state_file(self) -> Path:
        return self.state / "run_state.json"

    @property
    def run_log_file(self) -> Path:
        return self.logs / "run.jsonl"

    @property
    def agent_calls_file(self) -> Path:
        return self.logs / "agent_calls.jsonl"


class WorkspaceManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create(self, objective: str) -> WorkspacePaths:
        run_id = f"run_{day_stamp()}_{short_uuid()}_{slugify(objective)}"
        root = self.settings.workspace_root / run_id
        paths = WorkspacePaths(
            root=root,
            artifacts=root / "artifacts",
            cache_html=root / "cache" / "html",
            cache_pdf=root / "cache" / "pdf",
            cache_screenshots=root / "cache" / "screenshots",
            logs=root / "logs",
            state=root / "state",
        )
        for directory in (
            paths.artifacts,
            paths.cache_html,
            paths.cache_pdf,
            paths.cache_screenshots,
            paths.logs,
            paths.state,
        ):
            directory.mkdir(parents=True, exist_ok=False)

        return paths
