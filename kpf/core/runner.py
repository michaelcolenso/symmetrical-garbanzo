from __future__ import annotations

from pathlib import Path

import orjson

from kpf.config.settings import Settings
from kpf.core.clock import utc_timestamp
from kpf.core.logging import log_event
from kpf.core.workspace import WorkspaceManager, WorkspacePaths


class RunInitializer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.workspace_manager = WorkspaceManager(settings)

    def initialize(self, objective: str) -> WorkspacePaths:
        paths = self.workspace_manager.create(objective)
        self._write_initial_state(paths, objective)
        self._write_config_snapshot(paths)
        log_event(paths.run_log_file, "run.initialized", {"objective": objective})
        return paths

    def _write_initial_state(self, paths: WorkspacePaths, objective: str) -> None:
        state = {
            "run_id": paths.root.name,
            "objective": objective,
            "stage": "INIT",
            "status": "running",
            "created_at": utc_timestamp(),
        }
        paths.run_state_file.write_bytes(orjson.dumps(state, option=orjson.OPT_INDENT_2))

    def _write_config_snapshot(self, paths: WorkspacePaths) -> None:
        cfg_path = paths.root / "config.json"
        cfg_path.write_bytes(orjson.dumps(self.settings.model_dump(mode="json"), option=orjson.OPT_INDENT_2))
