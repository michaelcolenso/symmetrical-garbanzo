from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class EvidenceThresholds(BaseModel):
    min_sources: int = 15
    min_pain_quotes: int = 5
    min_spend_signals: int = 3
    min_competitors: int = 3
    min_authority_sources: int = 2


class OpportunityThresholds(BaseModel):
    total_score_min: int = 38
    pain_min: int = 7
    spend_min: int = 5
    solo_feasibility_min: int = 7


class Thresholds(BaseModel):
    evidence: EvidenceThresholds = Field(default_factory=EvidenceThresholds)
    opportunity: OpportunityThresholds = Field(default_factory=OpportunityThresholds)


class Settings(BaseModel):
    workspace_root: Path = Path("workspaces")
    timezone: str = "UTC"
    thresholds: Thresholds = Field(default_factory=Thresholds)
    config_path: Optional[Path] = None
