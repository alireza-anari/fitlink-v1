"""Generate ignored local/CI-only credentials without printing their values."""

import secrets
import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else ".env")
if path.exists():
    raise SystemExit("Refusing to overwrite an existing environment file")
values = {
    "POSTGRES_PASSWORD": secrets.token_urlsafe(32),
    "MINIO_ROOT_USER": "root-" + secrets.token_hex(8),
    "MINIO_ROOT_PASSWORD": secrets.token_urlsafe(32),
    "MINIO_APP_ACCESS_KEY": "app-" + secrets.token_hex(8),
    "MINIO_APP_SECRET_KEY": secrets.token_urlsafe(32),
    "WEB_PORT": "8001",
    "POSTGRES_HOST_PORT": "5434",
    "REDIS_HOST_PORT": "6381",
    "MINIO_HOST_PORT": "9100",
    "MINIO_CONSOLE_HOST_PORT": "9101",
}
path.write_text("".join(f"{key}={value}\n" for key, value in values.items()))
path.chmod(0o600)
