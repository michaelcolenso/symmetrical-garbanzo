"""Shared pytest fixtures for KPF tests."""

from __future__ import annotations
import pytest
from pathlib import Path
from kpf.config.settings import Settings
from kpf.core.workspace import WorkspaceManager
from kpf.config.loader import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear the lru_cache on get_settings before each test.

    Without this, tests that modify environment variables will see
    stale cached settings from prior tests.
    """
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def tmp_settings(tmp_path: Path) -> Settings:
    """Return a Settings instance pointing to a temporary workspace base."""
    return Settings(workspace_base=tmp_path / "workspaces")


@pytest.fixture
def tmp_manager(tmp_settings: Settings) -> WorkspaceManager:
    """Return a WorkspaceManager backed by a temporary workspace base."""
    return WorkspaceManager(tmp_settings)
