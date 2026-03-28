"""WorkspaceManager — creates and resolves all paths for a run.

All file paths in the system must be obtained through workspace helpers.
No code outside this module should construct raw paths to workspace subdirs.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from kpf.core.ids import make_run_id
from kpf.config.settings import Settings


# Canonical subdirectory names — never use string literals elsewhere
SUBDIR_CACHE = "cache"
SUBDIR_ARTIFACTS = "artifacts"
SUBDIR_LOGS = "logs"
SUBDIR_STATE = "state"

# Cache subdirectories
CACHE_HTML = "html"
CACHE_PDF = "pdf"
CACHE_SCREENSHOTS = "screenshots"


@dataclass
class WorkspacePaths:
    """All resolved absolute paths for a single run.

    Construct via WorkspaceManager.create_run() or .open_run().
    Never instantiate directly in application code.
    """

    run_id: str
    root: Path
    cache: Path
    artifacts: Path
    logs: Path
    state: Path

    # Cache subdirs
    cache_html: Path
    cache_pdf: Path
    cache_screenshots: Path

    def artifact(self, name: str) -> Path:
        """Resolve a named artifact path under artifacts/."""
        return self.artifacts / name

    def log_file(self, name: str) -> Path:
        """Resolve a named log file path under logs/."""
        return self.logs / name

    def state_file(self, name: str) -> Path:
        """Resolve a named state file under state/."""
        return self.state / name

    @property
    def run_state_path(self) -> Path:
        """Canonical path for the run state JSON file."""
        return self.state / "run.json"

    @property
    def events_log_path(self) -> Path:
        """Canonical path for the structured events log."""
        return self.logs / "events.jsonl"

    @property
    def agent_calls_log_path(self) -> Path:
        """Canonical path for agent call logs."""
        return self.logs / "agent_calls.jsonl"


class WorkspaceManager:
    """Creates and opens run workspaces."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base = Path(settings.workspace_base).resolve()

    @property
    def base(self) -> Path:
        return self._base

    def create_run(self, date_str: str | None = None) -> WorkspacePaths:
        """Create a new run workspace and return its resolved paths.

        This is the primary entry point for starting a new run.
        Creates the workspace_base if it does not exist, generates a
        sequential run ID, creates all subdirectories, and returns
        the fully-resolved WorkspacePaths.

        Args:
            date_str: Optional YYYYMMDD date override for testing.

        Returns:
            WorkspacePaths for the newly created run.

        Raises:
            FileExistsError: If the generated run directory already exists
                             (should not happen under normal operation).
        """
        self._base.mkdir(parents=True, exist_ok=True)
        run_id = make_run_id(self._base, date_str=date_str)
        run_root = self._base / run_id

        if run_root.exists():
            raise FileExistsError(
                f"Workspace already exists: {run_root}. "
                "This is unexpected — check for concurrent runs."
            )

        paths = self._build_paths(run_id, run_root)
        self._create_dirs(paths)
        return paths

    def open_run(self, run_id: str) -> WorkspacePaths:
        """Open an existing run workspace by run_id.

        Args:
            run_id: The run identifier, e.g. 'run_20260328_001'.

        Returns:
            WorkspacePaths for the existing run.

        Raises:
            FileNotFoundError: If the run directory does not exist.
        """
        run_root = self._base / run_id
        if not run_root.exists():
            raise FileNotFoundError(
                f"Workspace not found: {run_root}. "
                "Check the run_id and workspace_base setting."
            )
        return self._build_paths(run_id, run_root)

    def list_runs(self) -> list[str]:
        """Return all run IDs in workspace_base, sorted chronologically."""
        if not self._base.exists():
            return []
        return sorted(
            entry.name
            for entry in self._base.iterdir()
            if entry.is_dir() and entry.name.startswith("run_")
        )

    @staticmethod
    def _build_paths(run_id: str, root: Path) -> WorkspacePaths:
        cache = root / SUBDIR_CACHE
        return WorkspacePaths(
            run_id=run_id,
            root=root,
            cache=cache,
            artifacts=root / SUBDIR_ARTIFACTS,
            logs=root / SUBDIR_LOGS,
            state=root / SUBDIR_STATE,
            cache_html=cache / CACHE_HTML,
            cache_pdf=cache / CACHE_PDF,
            cache_screenshots=cache / CACHE_SCREENSHOTS,
        )

    @staticmethod
    def _create_dirs(paths: WorkspacePaths) -> None:
        """Create all required subdirectories for a run."""
        for d in [
            paths.root,
            paths.cache,
            paths.cache_html,
            paths.cache_pdf,
            paths.cache_screenshots,
            paths.artifacts,
            paths.logs,
            paths.state,
        ]:
            d.mkdir(parents=True, exist_ok=True)
