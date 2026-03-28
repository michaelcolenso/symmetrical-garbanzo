from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_timestamp() -> str:
    return utc_now().isoformat()


def day_stamp() -> str:
    return utc_now().strftime("%Y%m%d")
