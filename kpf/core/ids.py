"""ID generation for KPF entities.

All IDs are deterministic, human-readable, and sortable by time.
Run IDs encode the date and a per-day sequence number.
"""

from __future__ import annotations
from pathlib import Path
import re
from kpf.core.clock import date_slug, utc_today


_RUN_ID_PATTERN = re.compile(r"^run_(\d{8})_(\d{3})$")


def make_run_id(workspace_base: Path, date_str: str | None = None) -> str:
    """Generate the next sequential run ID for today.

    Scans workspace_base for existing run directories matching
    run_YYYYMMDD_NNN and returns the next number in the sequence.

    Args:
        workspace_base: The root workspace directory (may not yet exist).
        date_str: Optional YYYYMMDD override (for testing).

    Returns:
        A string like 'run_20260328_001'.
    """
    today = date_str or date_slug(utc_today())
    prefix = f"run_{today}_"

    existing_nums: list[int] = []
    if workspace_base.exists():
        for entry in workspace_base.iterdir():
            if entry.is_dir() and entry.name.startswith(prefix):
                m = _RUN_ID_PATTERN.match(entry.name)
                if m and m.group(1) == today:
                    existing_nums.append(int(m.group(2)))

    next_num = (max(existing_nums) + 1) if existing_nums else 1
    return f"run_{today}_{next_num:03d}"


def make_task_id(run_id: str, task_type: str, sequence: int) -> str:
    """Generate a task ID scoped to a run.

    Example: 'run_20260328_001__niche_research__001'
    """
    return f"{run_id}__{task_type}__{sequence:03d}"


def make_source_id(run_id: str, sequence: int) -> str:
    """Generate a source ID scoped to a run."""
    return f"{run_id}__src__{sequence:03d}"


def make_claim_id(run_id: str, sequence: int) -> str:
    """Generate a claim ID scoped to a run."""
    return f"{run_id}__claim__{sequence:03d}"


def make_artifact_id(run_id: str, artifact_type: str) -> str:
    """Generate an artifact ID scoped to a run."""
    return f"{run_id}__artifact__{artifact_type}"
