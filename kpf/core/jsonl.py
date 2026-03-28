from __future__ import annotations

from pathlib import Path
from typing import Any

import orjson


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as handle:
        handle.write(orjson.dumps(record))
        handle.write(b"\n")
