#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$APP_DIR/dist"
WEB_ROOT="/var/www/titan-crm"
RELEASES_DIR="$WEB_ROOT/releases"
RELEASE_DIR="$RELEASES_DIR/$(date -u +%Y%m%dT%H%M%SZ)-$$"
NEXT_LINK="$WEB_ROOT/.current-$$"

if [[ ! -f "$DIST_DIR/index.html" ]]; then
    echo "Missing $DIST_DIR/index.html; run npm run build first." >&2
    exit 1
fi

install -d -m 0755 "$RELEASES_DIR" "$RELEASE_DIR"
cp -a "$DIST_DIR/." "$RELEASE_DIR/"
chmod -R a+rX "$RELEASE_DIR"
ln -s "$RELEASE_DIR" "$NEXT_LINK"
mv -Tf "$NEXT_LINK" "$WEB_ROOT/current"

echo "Published static CRM release: $RELEASE_DIR"
