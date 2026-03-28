"""KPF runtime configuration.

Values are loaded from environment variables (prefixed KPF_) or a .env file.
All thresholds and paths are configurable — no hardcoded values in business logic.
"""

from __future__ import annotations
from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """KPF runtime configuration loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_prefix="KPF_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    workspace_base: Path = Field(
        default=Path("./workspaces"),
        description="Root directory for all run workspaces.",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging verbosity: DEBUG, INFO, WARNING, ERROR.",
    )

    # Optional in M1, required from M4 onward
    anthropic_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("ANTHROPIC_API_KEY", "KPF_ANTHROPIC_API_KEY"),
        description="Anthropic API key for LLM calls.",
    )

    # Evidence gate thresholds — configurable, not hardcoded
    gate_min_sources: int = Field(default=15)
    gate_min_pain_quotes: int = Field(default=5)
    gate_min_spend_signals: int = Field(default=3)
    gate_min_competitors: int = Field(default=3)
    gate_min_authority_sources: int = Field(default=2)

    # Scoring thresholds
    score_min_total: float = Field(default=38.0)
    score_min_pain: float = Field(default=7.0)
    score_min_spend: float = Field(default=5.0)
    score_min_solo_feasibility: float = Field(default=7.0)
