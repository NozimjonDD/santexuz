#!/usr/bin/env bash
# Run only on the runtime/test machine, from the backend directory.
set -euo pipefail
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
python manage.py seed_pilot
python manage.py test --settings=project_backend.settings.test
