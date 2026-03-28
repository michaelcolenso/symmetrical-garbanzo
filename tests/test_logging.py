"""Tests for kpf.core.logging."""

from __future__ import annotations
import logging
from pathlib import Path
import orjson
import pytest
from kpf.core.logging import configure_logging, get_logger, JsonlFileHandler


@pytest.fixture(autouse=True)
def reset_kpf_logger():
    """Clear kpf logger handlers before and after each test."""
    logger = logging.getLogger("kpf")
    logger.handlers.clear()
    yield
    logger.handlers.clear()


class TestConfigureLogging:
    def test_adds_handler_to_kpf_logger(self):
        configure_logging("INFO")
        logger = logging.getLogger("kpf")
        assert len(logger.handlers) > 0

    def test_sets_log_level(self):
        configure_logging("DEBUG")
        logger = logging.getLogger("kpf")
        assert logger.level == logging.DEBUG

    def test_does_not_duplicate_handlers_on_repeat_call(self):
        configure_logging("INFO")
        handler_count = len(logging.getLogger("kpf").handlers)
        configure_logging("INFO")
        assert len(logging.getLogger("kpf").handlers) == handler_count

    def test_adds_jsonl_handler_when_path_given(self, tmp_path):
        jsonl_path = tmp_path / "events.jsonl"
        configure_logging("INFO", jsonl_path=jsonl_path)
        logger = logging.getLogger("kpf")
        jsonl_handlers = [h for h in logger.handlers if isinstance(h, JsonlFileHandler)]
        assert len(jsonl_handlers) == 1

    def test_no_jsonl_handler_without_path(self):
        configure_logging("INFO")
        logger = logging.getLogger("kpf")
        jsonl_handlers = [h for h in logger.handlers if isinstance(h, JsonlFileHandler)]
        assert len(jsonl_handlers) == 0

    def test_propagation_disabled(self):
        configure_logging("INFO")
        logger = logging.getLogger("kpf")
        assert logger.propagate is False


class TestJsonlFileHandler:
    def test_creates_file_on_init(self, tmp_path):
        path = tmp_path / "test.jsonl"
        handler = JsonlFileHandler(path)
        handler.close()
        assert path.exists()

    def test_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "nested" / "dir" / "test.jsonl"
        handler = JsonlFileHandler(path)
        handler.close()
        assert path.exists()

    def test_writes_valid_json_record(self, tmp_path):
        path = tmp_path / "test.jsonl"
        handler = JsonlFileHandler(path)

        logger = logging.getLogger("kpf.test_handler")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.info("test message")
        handler.close()

        lines = path.read_bytes().splitlines()
        assert len(lines) >= 1
        record = orjson.loads(lines[0])
        assert "ts" in record
        assert "level" in record
        assert "logger" in record
        assert "msg" in record

    def test_record_has_correct_level(self, tmp_path):
        path = tmp_path / "test.jsonl"
        handler = JsonlFileHandler(path)

        logger = logging.getLogger("kpf.test_level")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.warning("warn message")
        handler.close()

        lines = path.read_bytes().splitlines()
        record = orjson.loads(lines[0])
        assert record["level"] == "WARNING"

    def test_record_message_content(self, tmp_path):
        path = tmp_path / "test.jsonl"
        handler = JsonlFileHandler(path)

        logger = logging.getLogger("kpf.test_msg")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.info("hello world")
        handler.close()

        lines = path.read_bytes().splitlines()
        record = orjson.loads(lines[0])
        assert record["msg"] == "hello world"

    def test_extra_fields_included(self, tmp_path):
        path = tmp_path / "test.jsonl"
        handler = JsonlFileHandler(path)

        logger = logging.getLogger("kpf.test_extra")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.info("event", extra={"run_id": "run_20240101_001", "stage": "INIT"})
        handler.close()

        lines = path.read_bytes().splitlines()
        record = orjson.loads(lines[0])
        assert record["run_id"] == "run_20240101_001"
        assert record["stage"] == "INIT"

    def test_appends_multiple_records(self, tmp_path):
        path = tmp_path / "test.jsonl"
        handler = JsonlFileHandler(path)

        logger = logging.getLogger("kpf.test_append")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.info("first")
        logger.info("second")
        logger.info("third")
        handler.close()

        lines = path.read_bytes().splitlines()
        assert len(lines) == 3


class TestGetLogger:
    def test_returns_logger(self):
        logger = get_logger("test")
        assert isinstance(logger, logging.Logger)

    def test_name_is_prefixed(self):
        logger = get_logger("mymodule")
        assert logger.name == "kpf.mymodule"

    def test_nested_name(self):
        logger = get_logger("agents.niche_research")
        assert logger.name == "kpf.agents.niche_research"
