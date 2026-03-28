"""Clock helpers — all time values in the system use these functions.

Never call datetime.now() or datetime.utcnow() directly in application code.
Always use utc_now() from this module so tests can monkeypatch time.
"""

from __future__ import annotations
from datetime import datetime, date, timezone


def utc_now() -> datetime:
    """Return the current UTC datetime with timezone info."""
    return datetime.now(tz=timezone.utc)


def utc_today() -> date:
    """Return today's UTC date."""
    return utc_now().date()


def format_iso(dt: datetime) -> str:
    """Format a datetime as ISO-8601 string with UTC offset."""
    return dt.isoformat()


def timestamp_ms() -> int:
    """Return current UTC time as integer milliseconds since epoch."""
    return int(utc_now().timestamp() * 1000)


def date_slug(d: date | None = None) -> str:
    """Return a date as YYYYMMDD string for use in IDs and paths."""
    target = d if d is not None else utc_today()
    return target.strftime("%Y%m%d")
