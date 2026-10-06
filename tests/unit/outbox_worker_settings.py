"""Private subprocess fixture: connect only to pytest's isolated database."""

import os

from config.settings.test import *  # noqa: F403
from config.settings.test import DATABASES

if os.environ.get("C02_WORKER_TEST_DATABASE") != "test_fitlink":
    raise ValueError("Isolated pytest database required")
DATABASES["default"]["NAME"] = "test_fitlink"
