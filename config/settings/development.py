from .base import *  # noqa: F403

DEBUG = True
if DATABASES["default"]["HOST"] not in {"db", "localhost", "127.0.0.1"}:  # noqa: F405
    env.invalid("POSTGRES_HOST")  # noqa: F405
if DATABASES["default"]["NAME"] != "fitlink":  # noqa: F405
    env.invalid("POSTGRES_DB")  # noqa: F405
