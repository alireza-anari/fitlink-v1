import logging
import time
import uuid

from .logging import request_id

logger = logging.getLogger("fitlink.request")


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        header = request.headers.get("X-Request-ID", "")
        try:
            if len(header) != 36:
                raise ValueError
            identifier = str(uuid.UUID(header))
        except (ValueError, AttributeError):
            identifier = str(uuid.uuid4())
        token = request_id.set(identifier)
        request.request_id = identifier
        started = time.monotonic()
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = identifier
            match = getattr(request, "resolver_match", None)
            # Route patterns reveal no query values, path IDs or arbitrary paths.
            route = str(match.route)[:160] if match else "<unmatched>"
            method = (
                request.method
                if request.method
                in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
                else "<other>"
            )
            logger.info(
                "request",
                extra={
                    "event": "request.completed",
                    "method": method,
                    "route": route,
                    "status": response.status_code,
                    "duration_ms": round((time.monotonic() - started) * 1000, 2),
                    "request_id": identifier,
                },
            )
            return response
        except Exception:
            logger.exception(
                "request", extra={"event": "request.failed", "request_id": identifier}
            )
            raise
        finally:
            request_id.reset(token)
