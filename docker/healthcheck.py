import os
import sys
from urllib.request import urlopen


def main() -> int:
    kind = sys.argv[1]
    if kind == "web":
        try:
            with urlopen("http://127.0.0.1:8000/health/ready/", timeout=5) as response:
                return 0 if response.status == 200 else 1
        except Exception:
            return 1
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    import django

    django.setup()
    if kind == "db":
        from config.health import database_available

        return 0 if database_available() else 1
    if kind == "worker":
        import socket

        from config.celery import app

        return (
            0
            if app.control.ping(
                timeout=2, destination=["foundation@" + socket.gethostname()]
            )
            else 1
        )
    if kind == "beat":
        from pathlib import Path

        schedule = Path("/var/lib/celery/celerybeat-schedule")
        running = b"beat" in Path("/proc/1/cmdline").read_bytes()
        return 0 if schedule.exists() and running else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
