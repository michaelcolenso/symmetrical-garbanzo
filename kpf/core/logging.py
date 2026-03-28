from __future__ import annotations

from pathlib import Path
from typing import Any

from kpf.core.clock import utc_timestamp
from kpf.core.jsonl import append_jsonl


def log_event(log_file: Path, event: str, payload: dict[str, Any] | None = None) -> None:
    append_jsonl(
        log_file,
        {
            "ts": utc_timestamp(),
            "event": event,
            "payload": payload or {},
        },
    )
