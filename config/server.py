"""ASGI runtime entrypoint with safe logging before Uvicorn startup."""

import logging
import os

import django
import uvicorn
from django.conf import settings


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()
    logging.getLogger("fitlink.runtime").info(
        "startup", extra={"event": "process.started", "process_role": "web"}
    )
    uvicorn.run(
        "config.asgi:application",
        host="0.0.0.0",
        port=8000,
        access_log=False,
        proxy_headers=False,
        log_config=settings.LOGGING,
    )


if __name__ == "__main__":
    main()
