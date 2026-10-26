import json
import logging
import re
from contextvars import ContextVar
from datetime import UTC, datetime

# Holds the ID of the request being handled ("-" outside of a request).
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

# Extra fields that the request logger can attach to a log record.
_EXTRA_FIELDS = ("method", "path", "status_code", "duration_ms")

_SENSITIVE_PATTERN = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|authorization)\b"
    r"""(["']?\s*[=:]\s*["']?)(?:bearer\s+)?[^\s,;&"']+"""
)


def redact(text: str) -> str:
    """Mask values that follow words like password, token or authorization."""
    return _SENSITIVE_PATTERN.sub(r"\1\2***", text)


class RequestIdFilter(logging.Filter):
    """Adds the current request ID to every record that does not have one."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.__dict__["request_id"] = request_id_ctx.get()
        return True


class JsonFormatter(logging.Formatter):
    """Formats a log record as a single line of JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": redact(record.getMessage()),
            "request_id": getattr(record, "request_id", "-"),
        }
        for field in _EXTRA_FIELDS:
            if hasattr(record, field):
                payload[field] = getattr(record, field)
        if record.exc_info:
            payload["exception"] = redact(self.formatException(record.exc_info))
        return json.dumps(payload, ensure_ascii=False, default=str)


class _AppStreamHandler(logging.StreamHandler):
    """Marker class, so setup_logging can replace its own handler safely."""


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger. Safe to call more than once."""
    handler = _AppStreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    for existing in [h for h in root.handlers if isinstance(h, _AppStreamHandler)]:
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(level)

    # Send uvicorn's own logs through the same handler and format.
    for name in ("uvicorn", "uvicorn.error"):
        server_logger = logging.getLogger(name)
        server_logger.handlers.clear()
        server_logger.propagate = True
        server_logger.setLevel(logging.NOTSET)

    # Our middleware already logs every request, so skip uvicorn's access log.
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers.clear()
    access_logger.propagate = False
    access_logger.disabled = True
