"""Bounded same-origin private upload parsing."""

from rest_framework import exceptions, parsers  # type: ignore[import-untyped]

from .storage import limited_spool
from .validation import MAX_BYTES


class BoundedMultipartParser(parsers.MultiPartParser):
    def parse(self, stream, media_type=None, parser_context=None):
        context = parser_context or {}
        request = context.get("request")
        if request is None:
            raise exceptions.ParseError("Invalid request")
        try:
            with limited_spool(stream, MAX_BYTES) as body:
                body.seek(0, 2)
                size = body.tell()
                body.seek(0)
                request.META["CONTENT_LENGTH"] = str(size)
                return super().parse(body, media_type, context)
        except ValueError:
            raise exceptions.ParseError("Invalid request") from None
