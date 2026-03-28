from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from kpf.config.settings import Settings


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Config at {path} must be a YAML mapping.")
    return loaded


def load_settings(config_path: Path | None = None) -> Settings:
    defaults_path = Path(__file__).with_name("defaults.yaml")
    defaults = _read_yaml(defaults_path)
    user_cfg = _read_yaml(config_path) if config_path else {}
    merged = {**defaults, **user_cfg}
    settings = Settings.model_validate(merged)
    settings.config_path = config_path
    return settings
