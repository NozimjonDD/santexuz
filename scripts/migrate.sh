#!/usr/bin/env bash
set -euo pipefail
echo 'Retired. Production schema changes use the separate migrator through deploy/ubuntu/deploy.py release.' >&2
echo 'For an isolated development database use python manage.py migrate.' >&2
exit 2
