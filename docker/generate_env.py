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
values.update(
    {
        "POSTGRES_DB": "fitlink",
        "POSTGRES_USER": "fitlink",
        "POSTGRES_HOST": "127.0.0.1",
        "POSTGRES_PORT": values["POSTGRES_HOST_PORT"],
        "REDIS_URL": f"redis://127.0.0.1:{values['REDIS_HOST_PORT']}/0",
        "CELERY_BROKER_URL": f"redis://127.0.0.1:{values['REDIS_HOST_PORT']}/1",
        "CELERY_RESULT_BACKEND": f"redis://127.0.0.1:{values['REDIS_HOST_PORT']}/2",
        "CHANNEL_REDIS_URL": f"redis://127.0.0.1:{values['REDIS_HOST_PORT']}/3",
        "STORAGE_BACKEND": "s3",
        "S3_ENDPOINT_URL": f"http://127.0.0.1:{values['MINIO_HOST_PORT']}",
        "S3_BUCKET_NAME": "fitlink-private",
        "S3_REGION": "us-east-1",
        "S3_ACCESS_KEY_ID": values["MINIO_APP_ACCESS_KEY"],
        "S3_SECRET_ACCESS_KEY": values["MINIO_APP_SECRET_KEY"],
    }
)
path.write_text("".join(f"{key}={value}\n" for key, value in values.items()))
path.chmod(0o600)
