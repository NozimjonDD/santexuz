#!/usr/bin/env bash
# Run on the verification machine. PowerShell: python scripts/verify.py
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$root"

if [[ -n "${PYTHON:-}" ]]; then
    interpreter="$PYTHON"
elif [[ -n "${VIRTUAL_ENV:-}" ]]; then
    interpreter="python"
elif [[ -x .venv/bin/python ]]; then
    interpreter=".venv/bin/python"
elif [[ -f .venv/Scripts/python.exe ]]; then
    interpreter=".venv/Scripts/python.exe"
elif [[ -x venv/bin/python ]]; then
    interpreter="venv/bin/python"
elif [[ -f venv/Scripts/python.exe ]]; then
    interpreter="venv/Scripts/python.exe"
else
    interpreter="python"
fi

exec "$interpreter" scripts/verify.py
