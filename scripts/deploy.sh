#!/usr/bin/env bash
# Ubuntu server only; see deploy/ubuntu/README.md.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$root/deploy/ubuntu/deploy.py" "$@"
