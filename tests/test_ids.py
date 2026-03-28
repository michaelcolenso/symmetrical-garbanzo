"""Tests for kpf.core.ids."""

from __future__ import annotations
import re
from pathlib import Path
import pytest
from kpf.core.ids import (
    make_run_id,
    make_task_id,
    make_source_id,
    make_claim_id,
    make_artifact_id,
)


class TestMakeRunId:
    def test_first_run_is_001(self, tmp_path):
        run_id = make_run_id(tmp_path, date_str="20240101")
        assert run_id == "run_20240101_001"

    def test_sequential_with_existing_dir(self, tmp_path):
        (tmp_path / "run_20240101_001").mkdir()
        run_id = make_run_id(tmp_path, date_str="20240101")
        assert run_id == "run_20240101_002"

    def test_sequential_skips_gaps(self, tmp_path):
        (tmp_path / "run_20240101_001").mkdir()
        (tmp_path / "run_20240101_002").mkdir()
        (tmp_path / "run_20240101_003").mkdir()
        run_id = make_run_id(tmp_path, date_str="20240101")
        assert run_id == "run_20240101_004"

    def test_different_date_resets_to_001(self, tmp_path):
        (tmp_path / "run_20240101_001").mkdir()
        run_id = make_run_id(tmp_path, date_str="20240102")
        assert run_id == "run_20240102_001"

    def test_ignores_dirs_from_other_dates(self, tmp_path):
        (tmp_path / "run_20240101_001").mkdir()
        (tmp_path / "run_20240101_002").mkdir()
        run_id = make_run_id(tmp_path, date_str="20240201")
        assert run_id == "run_20240201_001"

    def test_ignores_non_run_dirs(self, tmp_path):
        (tmp_path / "some_other_dir").mkdir()
        (tmp_path / "not_a_run").mkdir()
        run_id = make_run_id(tmp_path, date_str="20240101")
        assert run_id == "run_20240101_001"

    def test_nonexistent_base_returns_001(self, tmp_path):
        base = tmp_path / "missing"
        run_id = make_run_id(base, date_str="20240101")
        assert run_id == "run_20240101_001"

    def test_format_matches_pattern(self, tmp_path):
        run_id = make_run_id(tmp_path, date_str="20991231")
        assert re.match(r"^run_\d{8}_\d{3}$", run_id)

    def test_sequence_is_zero_padded_3_digits(self, tmp_path):
        run_id = make_run_id(tmp_path, date_str="20240101")
        assert run_id.split("_")[-1] == "001"


class TestMakeTaskId:
    def test_format(self):
        task_id = make_task_id("run_20240101_001", "niche_research", 1)
        assert task_id == "run_20240101_001__niche_research__001"

    def test_sequence_padding(self):
        task_id = make_task_id("run_20240101_001", "pain_scout", 42)
        assert task_id == "run_20240101_001__pain_scout__042"


class TestMakeSourceId:
    def test_format(self):
        source_id = make_source_id("run_20240101_001", 1)
        assert source_id == "run_20240101_001__src__001"

    def test_sequence_padding(self):
        source_id = make_source_id("run_20240101_001", 15)
        assert source_id == "run_20240101_001__src__015"


class TestMakeClaimId:
    def test_format(self):
        claim_id = make_claim_id("run_20240101_001", 3)
        assert claim_id == "run_20240101_001__claim__003"


class TestMakeArtifactId:
    def test_format(self):
        artifact_id = make_artifact_id("run_20240101_001", "blueprint")
        assert artifact_id == "run_20240101_001__artifact__blueprint"

    def test_format_with_underscores(self):
        artifact_id = make_artifact_id("run_20240101_001", "sales_page")
        assert artifact_id == "run_20240101_001__artifact__sales_page"
