"""Tests for kpf.core.clock."""

from __future__ import annotations
import re
from datetime import datetime, date, timezone
import pytest
from kpf.core.clock import utc_now, utc_today, format_iso, timestamp_ms, date_slug


class TestUtcNow:
    def test_returns_datetime(self):
        result = utc_now()
        assert isinstance(result, datetime)

    def test_has_timezone_info(self):
        result = utc_now()
        assert result.tzinfo is not None

    def test_is_utc(self):
        result = utc_now()
        assert result.tzinfo == timezone.utc


class TestUtcToday:
    def test_returns_date(self):
        result = utc_today()
        assert isinstance(result, date)

    def test_not_datetime(self):
        result = utc_today()
        # date instances that are also datetime return True for isinstance(x, date)
        # but utc_today() should return a pure date
        assert type(result) is date


class TestFormatIso:
    def test_returns_string(self):
        result = format_iso(utc_now())
        assert isinstance(result, str)

    def test_roundtrip(self):
        original = utc_now()
        formatted = format_iso(original)
        parsed = datetime.fromisoformat(formatted)
        assert parsed == original

    def test_contains_timezone_offset(self):
        result = format_iso(utc_now())
        assert "+" in result or result.endswith("Z") or result.endswith("+00:00")


class TestTimestampMs:
    def test_returns_int(self):
        result = timestamp_ms()
        assert isinstance(result, int)

    def test_reasonable_value(self):
        # Should be well past year 2000 (946684800000 ms) and before 2100 (4102444800000 ms)
        result = timestamp_ms()
        assert result > 946684800000
        assert result < 4102444800000

    def test_monotonically_increasing(self):
        t1 = timestamp_ms()
        t2 = timestamp_ms()
        assert t2 >= t1


class TestDateSlug:
    def test_format_is_eight_digits(self):
        result = date_slug()
        assert re.match(r"^\d{8}$", result)

    def test_with_specific_date(self):
        d = date(2026, 3, 28)
        result = date_slug(d)
        assert result == "20260328"

    def test_with_leap_day(self):
        d = date(2024, 2, 29)
        result = date_slug(d)
        assert result == "20240229"

    def test_default_uses_today(self):
        result = date_slug()
        today = utc_today()
        expected = today.strftime("%Y%m%d")
        assert result == expected
