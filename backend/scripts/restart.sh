#!/usr/bin/env bash
set -euo pipefail
echo 'Retired. On Ubuntu use: sudo python3 deploy/ubuntu/deploy.py release' >&2
echo 'The release command performs backup, migrations, service restart and readiness checks.' >&2
exit 2
