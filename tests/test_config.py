"""Tests for kpf.config.settings and kpf.config.loader."""

from __future__ import annotations
from pathlib import Path
import pytest
from kpf.config.settings import Settings
from kpf.config.loader import get_settings


class TestSettingsDefaults:
    def test_workspace_base_default(self):
        s = Settings()
        assert s.workspace_base == Path("./workspaces")

    def test_log_level_default(self):
        s = Settings()
        assert s.log_level == "INFO"

    def test_anthropic_api_key_default_empty(self):
        s = Settings()
        assert s.anthropic_api_key == ""

    def test_gate_min_sources_default(self):
        s = Settings()
        assert s.gate_min_sources == 15

    def test_gate_min_pain_quotes_default(self):
        s = Settings()
        assert s.gate_min_pain_quotes == 5

    def test_gate_min_spend_signals_default(self):
        s = Settings()
        assert s.gate_min_spend_signals == 3

    def test_gate_min_competitors_default(self):
        s = Settings()
        assert s.gate_min_competitors == 3

    def test_gate_min_authority_sources_default(self):
        s = Settings()
        assert s.gate_min_authority_sources == 2

    def test_score_min_total_default(self):
        s = Settings()
        assert s.score_min_total == 38.0

    def test_score_min_pain_default(self):
        s = Settings()
        assert s.score_min_pain == 7.0

    def test_workspace_base_is_path(self):
        s = Settings()
        assert isinstance(s.workspace_base, Path)


class TestSettingsFromEnv:
    def test_log_level_from_env(self, monkeypatch):
        monkeypatch.setenv("KPF_LOG_LEVEL", "DEBUG")
        s = Settings()
        assert s.log_level == "DEBUG"

    def test_workspace_base_from_env(self, monkeypatch, tmp_path):
        monkeypatch.setenv("KPF_WORKSPACE_BASE", str(tmp_path))
        s = Settings()
        assert s.workspace_base == tmp_path

    def test_anthropic_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
        s = Settings()
        assert s.anthropic_api_key == "sk-test-key"

    def test_anthropic_api_key_from_kpf_prefixed_env(self, monkeypatch):
        monkeypatch.setenv("KPF_ANTHROPIC_API_KEY", "sk-kpf-key")
        s = Settings()
        assert s.anthropic_api_key == "sk-kpf-key"

    def test_gate_threshold_from_env(self, monkeypatch):
        monkeypatch.setenv("KPF_GATE_MIN_SOURCES", "20")
        s = Settings()
        assert s.gate_min_sources == 20

    def test_workspace_base_coerced_to_path(self, monkeypatch, tmp_path):
        monkeypatch.setenv("KPF_WORKSPACE_BASE", str(tmp_path))
        s = Settings()
        assert isinstance(s.workspace_base, Path)


class TestSettingsLoader:
    def test_get_settings_returns_settings(self):
        s = get_settings()
        assert isinstance(s, Settings)

    def test_get_settings_is_cached(self):
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_get_settings_cache_clear_returns_new_instance(self):
        s1 = get_settings()
        get_settings.cache_clear()
        s2 = get_settings()
        assert s1 is not s2

    def test_cache_clear_reflects_env_change(self, monkeypatch):
        s1 = get_settings()
        assert s1.log_level == "INFO"

        get_settings.cache_clear()
        monkeypatch.setenv("KPF_LOG_LEVEL", "DEBUG")
        s2 = get_settings()
        assert s2.log_level == "DEBUG"

    def test_model_copy_does_not_affect_cached(self, tmp_path):
        s = get_settings()
        s_copy = s.model_copy(update={"workspace_base": tmp_path})
        assert s_copy.workspace_base == tmp_path
        # Original cached instance is unchanged
        assert get_settings().workspace_base != tmp_path
