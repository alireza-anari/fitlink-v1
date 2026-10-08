"""Cap actual upload bodies before Django/CSRF can parse or spool them."""

from io import BytesIO
from tempfile import SpooledTemporaryFile

from django.conf import settings
from django.http import JsonResponse


def upload_body(path: str, method: str) -> bool:
    return (
        method == "POST"
        and path.startswith("/api/v1/profile-assets/")
        and path.endswith("/body/")
    )


def limit() -> int:
    return min(getattr(settings, "PROFILE_UPLOAD_MAX_BYTES", 10_000_000), 10_000_000)


class UploadBodyLimit:
    def __init__(self, application):
        self.application = application

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not upload_body(scope["path"], scope["method"]):
            return await self.application(scope, receive, send)
        size = 0
        with SpooledTemporaryFile(max_size=1_048_576, mode="w+b") as body:
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                chunk = message.get("body", b"")
                size += len(chunk)
                if size > limit():
                    await send(
                        {
                            "type": "http.response.start",
                            "status": 400,
                            "headers": [
                                (b"content-type", b"application/json"),
                                (b"cache-control", b"no-store"),
                                (b"x-content-type-options", b"nosniff"),
                            ],
                        }
                    )
                    await send(
                        {"type": "http.response.body", "body": b'{"status":"invalid"}'}
                    )
                    return
                body.write(chunk)
                if not message.get("more_body", False):
                    break
            body.seek(0)
            remaining = size
            delivered = False

            async def replay():
                nonlocal remaining, delivered
                if delivered:
                    return await receive()
                chunk = body.read(65536)
                remaining -= len(chunk)
                delivered = remaining == 0
                return {
                    "type": "http.request",
                    "body": chunk,
                    "more_body": not delivered,
                }

            # Actual measured bytes, never an untrusted Content-Length hint.
            scope = {
                **scope,
                "headers": [
                    (k, v)
                    for k, v in scope.get("headers", [])
                    if k.lower() != b"content-length"
                ]
                + [(b"content-length", str(size).encode())],
            }
            await self.application(scope, replay, send)


class UploadRequestLimit:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if upload_body(request.path, request.method):
            parts, size = [], 0
            while True:
                chunk = request.read(min(65536, limit() + 1 - size))
                size += len(chunk)
                if size > limit():
                    response = JsonResponse({"status": "invalid"}, status=400)
                    response["Cache-Control"] = "no-store"
                    return response
                parts.append(chunk)
                if not chunk:
                    break
            request._body = b"".join(parts)
            request._stream = BytesIO(request._body)
            request.META["CONTENT_LENGTH"] = str(size)
        return self.get_response(request)
