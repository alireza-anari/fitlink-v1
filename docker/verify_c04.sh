#!/bin/sh
set -eu
# This is Task 1's cumulative real-PostgreSQL gate. The eleven inherited
# current-source jobs and immutable full C03 verifier run independently.
sh docker/verify_c04_incremental.sh --task 4
uv run --frozen python manage.py makemigrations --check --dry-run --settings=config.settings.test
