import json
import logging

import pytest
from pydantic import ValidationError

from app.logging_config import (
    JsonFormatter,
    RequestIdFilter,
    redact,
    request_id_ctx,
    setup_logging,
)
from app.settings import Settings


def make_settings(**overrides):
    # Required database fields come from the environment, as in the app itself.
    return Settings(_env_file=None, **overrides)  # type: ignore[call-arg]


def make_record(message: str = "hello", **extra) -> logging.LogRecord:
    record = logging.LogRecord(
        "test.logger", logging.INFO, __file__, 1, message, None, None
    )
    record.__dict__.update(extra)
    return record


@pytest.fixture
def restore_root_logger():
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield
    root.handlers[:] = handlers
    root.setLevel(level)


@pytest.mark.parametrize("level", ["DEBUG", "WARNING", "ERROR"])
def test_setup_logging_applies_log_level(restore_root_logger, level):
    setup_logging(level)

    assert logging.getLogger().level == getattr(logging, level)


def test_setup_logging_does_not_duplicate_handler(restore_root_logger):
    setup_logging("INFO")
    setup_logging("INFO")

    json_handlers = [
        handler
        for handler in logging.getLogger().handlers
        if isinstance(handler.formatter, JsonFormatter)
    ]
    assert len(json_handlers) == 1


def test_log_level_defaults_to_info(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    assert make_settings().LOG_LEVEL == "INFO"


def test_log_level_is_read_from_environment_and_normalized(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "warning")

    assert make_settings().LOG_LEVEL == "WARNING"


def test_log_level_accepts_lowercase_value():
    assert make_settings(LOG_LEVEL="debug").LOG_LEVEL == "DEBUG"


def test_invalid_log_level_is_rejected():
    with pytest.raises(ValidationError):
        make_settings(LOG_LEVEL="verbose")


def test_json_formatter_outputs_required_fields():
    record = make_record("hello")
    RequestIdFilter().filter(record)

    entry = json.loads(JsonFormatter().format(record))

    assert entry["message"] == "hello"
    assert entry["level"] == "INFO"
    assert entry["logger"] == "test.logger"
    assert entry["request_id"] == "-"
    assert "timestamp" in entry


def test_filter_uses_request_id_from_context():
    token = request_id_ctx.set("ctx-123")
    try:
        record = make_record()
        RequestIdFilter().filter(record)
    finally:
        request_id_ctx.reset(token)

    assert json.loads(JsonFormatter().format(record))["request_id"] == "ctx-123"


def test_filter_keeps_explicit_request_id():
    token = request_id_ctx.set("ctx-123")
    try:
        record = make_record(request_id="explicit-1")
        RequestIdFilter().filter(record)
    finally:
        request_id_ctx.reset(token)

    assert json.loads(JsonFormatter().format(record))["request_id"] == "explicit-1"


def test_json_formatter_redacts_sensitive_values():
    record = make_record("login failed password=hunter2")
    RequestIdFilter().filter(record)

    output = JsonFormatter().format(record)

    assert "hunter2" not in output


@pytest.mark.parametrize(
    ("text", "secret"),
    [
        ("password=hunter2", "hunter2"),
        ("Authorization: Bearer abc.def", "abc.def"),
        ('{"token": "xyz123"}', "xyz123"),
        ("api_key=KEY123", "KEY123"),
    ],
)
def test_redact_masks_sensitive_values(text, secret):
    result = redact(text)

    assert secret not in result
    assert "***" in result
