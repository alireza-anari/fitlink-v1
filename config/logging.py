import json
import logging
import traceback
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path

from django.conf import settings

request_id: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Only explicit safe fields are emitted. Never interpolate arbitrary
        # third-party messages, exception text, locals or request payloads.
        value = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(record, "event", "runtime.event"),
            "request_id": getattr(record, "request_id", request_id.get()),
            "release_id": settings.RELEASE_ID,
        }
        for key in ("method", "route", "status", "duration_ms"):
            if hasattr(record, key):
                value[key] = getattr(record, key)
        if record.exc_info and record.exc_info[0]:
            value["error_class"] = record.exc_info[0].__name__
            value["frames"] = [
                {
                    "file": Path(frame.filename).name,
                    "line": frame.lineno,
                    "function": frame.name,
                }
                for frame in traceback.extract_tb(record.exc_info[2])
            ]
        return json.dumps(value, ensure_ascii=False)
