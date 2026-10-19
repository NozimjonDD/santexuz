#!/usr/bin/env bash
# Ubuntu server only. Optional arguments: --config /etc/<app>/deploy.ini
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$root/deploy/ubuntu/deploy.py" "$@" status
