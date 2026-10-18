"""Cross-platform verification entry point, using the invoking Python environment."""
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
STEPS = (
    ("Django configuration", ("check",)),
    ("Model and migration consistency", ("makemigrations", "--check", "--dry-run")),
    ("OpenAPI schema", ("spectacular", "--validate", "--fail-on-warn", "--file", "storage/logs/openapi-verified.yaml")),
    ("Apply migrations", ("migrate", "--noinput")),
    ("Pilot catalog", ("seed_pilot",)),
    ("Backend tests", ("test", "--settings=project_backend.settings.test")),
)


def main():
    for index, (label, arguments) in enumerate(STEPS, start=1):
        print(f"\n[{index}/{len(STEPS)}] {label}", flush=True)
        result = subprocess.run(
            [sys.executable, str(ROOT / "manage.py"), *arguments],
            cwd=ROOT,
            check=False,
        )
        if result.returncode:
            print(f"\nFAILED: {label} (exit {result.returncode}). See the error above.", file=sys.stderr)
            return result.returncode
    print("\nAll verification steps passed.", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
