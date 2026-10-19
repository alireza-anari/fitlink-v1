#!/bin/sh
set -eu
# Installed tasks are cumulative; reject attempts to select unimplemented work.
test "$#" -eq 2
test "$1" = --task
test "$2" = 1
uv run --frozen python docker/c04_gate.py tests/unit/c04 tests/integration/c04 tests/integration/c03/test_c03_migrations.py::test_optional_profiles_not_created -q --strict-markers --tb=short --show-capture=no
