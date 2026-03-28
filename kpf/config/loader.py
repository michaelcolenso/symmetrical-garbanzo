"""Settings loader — provides a cached settings singleton."""

from __future__ import annotations
from functools import lru_cache
from kpf.config.settings import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    Reads from environment and .env on first call; subsequent calls
    return the cached instance. Call get_settings.cache_clear() in tests
    to force re-evaluation with a fresh environment.
    """
    return Settings()


def load_settings() -> Settings:
    """Alias for get_settings(). Use in application code for clarity."""
    return get_settings()
