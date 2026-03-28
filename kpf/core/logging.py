"""KPF structured logging scaffold.

Two output channels:
1. JSONL file at <workspace>/logs/events.jsonl — structured, machine-readable
2. Rich console — human-readable CLI output

Use get_logger() to obtain a logger after the run workspace is available.
Use configure_logging() before a workspace exists (during startup) for console-only mode.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Any
import orjson
from rich.console import Console
from rich.logging import RichHandler
from kpf.core.clock import utc_now, format_iso


# Rich console writes to stderr; stdout is reserved for data output
_console = Console(stderr=True)

# Attributes always present on a LogRecord — skipped when copying extras
_LOGGING_BUILTIN_ATTRS = frozenset({
    "name", "msg", "args", "levelname", "levelno", "pathname",
    "filename", "module", "exc_info", "exc_text", "stack_info",
    "lineno", "funcName", "created", "msecs", "relativeCreated",
    "thread", "threadName", "processName", "process", "message",
    "taskName",
})


class JsonlFileHandler(logging.Handler):
    """Logging handler that appends structured JSONL records to a file.

    Each log record is written as a single JSON line with:
    - ts (ISO-8601 UTC)
    - level
    - logger name
    - message
    - any extra fields passed via the 'extra' kwarg
    """

    def __init__(self, path: Path) -> None:
        super().__init__()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path
        self._file = path.open("ab")  # binary for orjson; append mode

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry: dict[str, Any] = {
                "ts": format_iso(utc_now()),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
            }
            # Merge any extra fields attached to the record
            for key, val in record.__dict__.items():
                if key not in _LOGGING_BUILTIN_ATTRS and not key.startswith("_"):
                    try:
                        # Only include JSON-serializable extras
                        orjson.dumps(val)
                        entry[key] = val
                    except (TypeError, ValueError):
                        entry[key] = str(val)

            self._file.write(orjson.dumps(entry) + b"\n")
            self._file.flush()
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        try:
            self._file.close()
        finally:
            super().close()


def configure_logging(
    log_level: str,
    jsonl_path: Path | None = None,
) -> None:
    """Configure the root KPF logger.

    Call this once at startup from the CLI entrypoint, and again after
    the workspace is created to add the JSONL file handler.

    Args:
        log_level: String level name: DEBUG, INFO, WARNING, ERROR.
        jsonl_path: If provided, add a JSONL file handler for structured logging.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    root = logging.getLogger("kpf")
    root.setLevel(level)
    root.handlers.clear()  # Prevent duplicate handlers on repeated calls (tests)

    # Rich console handler — human-readable, goes to stderr
    rich_handler = RichHandler(
        console=_console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        markup=True,
    )
    rich_handler.setLevel(level)
    root.addHandler(rich_handler)

    # JSONL file handler — structured, appended to events.jsonl
    if jsonl_path is not None:
        file_handler = JsonlFileHandler(jsonl_path)
        file_handler.setLevel(logging.DEBUG)  # Always capture DEBUG to file
        root.addHandler(file_handler)

    # Prevent log records from bubbling to the root Python logger
    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'kpf' root logger.

    Args:
        name: Sub-logger name, e.g. 'workspace', 'cli.run', 'agents.niche_research'.

    Returns:
        A Logger that inherits handlers from 'kpf'.
    """
    return logging.getLogger(f"kpf.{name}")
