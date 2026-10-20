#!/bin/sh
set -eu
# Installed tasks are cumulative; reject attempts to select unimplemented work.
test "$#" -eq 2
test "$1" = --task
case "$2" in
  1|2|3|4|5) ;;
  *) exit 1 ;;
esac
if [ "$2" -ge 2 ]; then
uv run --frozen python manage.py sqlmigrate professionals 0018 --settings=config.settings.test
uv run --frozen python manage.py sqlmigrate governance 0015 --settings=config.settings.test
fi
if [ "$2" -ge 3 ]; then
uv run --frozen python manage.py sqlmigrate assets 0010 --settings=config.settings.test
fi
if [ "$2" -ge 4 ]; then
uv run --frozen python manage.py sqlmigrate marketplace 0001 --settings=config.settings.test
fi
if [ "$2" -ge 5 ]; then
uv run --frozen python manage.py sqlmigrate marketplace 0002 --settings=config.settings.test
export C04_SEARCH_EVIDENCE=1
fi
uv run --frozen python docker/c04_gate.py tests/unit/c04 tests/integration/c04 --ignore=tests/integration/c04/test_public_media_services.py tests/integration/c03/test_c03_migrations.py::test_optional_profiles_not_created -q --strict-markers --tb=short --show-capture=no
printf 'C04_TASK_ACCEPTANCE task=%s\n' "$2"
