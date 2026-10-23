"""Synthetic post commands always use actual account and profile authority."""

import importlib
import importlib.util
from uuid import uuid4

from django.utils import timezone


def command(name):
    module = "config.use_cases.public_content"
    assert importlib.util.find_spec(module), "Missing post/moderation composition"
    value = getattr(importlib.import_module(module), name, None)
    assert callable(value), "Missing post/moderation command: " + name
    return value


def draft(subject, text="آموزش حرکت"):
    from apps.professionals.post_contracts import PostInput

    return command("save_post")(
        subject.actor, None, PostInput(text), None, uuid4(), timezone.now()
    )
