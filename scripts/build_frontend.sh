#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/src/frontend"
DIST_DIR="$SRC_DIR/dist"
BACKEND_URL="${BALLSY_BACKEND_URL:-}"

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

cp "$SRC_DIR/templates/index.html" "$DIST_DIR/index.html"
cp -R "$SRC_DIR/static" "$DIST_DIR/static"

python3 - "$DIST_DIR/index.html" "$BACKEND_URL" <<'PY'
from pathlib import Path
import json
import sys

index_path = Path(sys.argv[1])
backend_url = sys.argv[2].rstrip("/")
content = index_path.read_text()
content = content.replace('"__BALLSY_BACKEND_URL__"', json.dumps(backend_url))
index_path.write_text(content)
PY

python3 - "$DIST_DIR/static/js/config.js" "$BACKEND_URL" <<'PY'
from pathlib import Path
import json
import sys

config_path = Path(sys.argv[1])
backend_url = sys.argv[2].rstrip("/")
config_path.write_text(f"window.BALLSY_BACKEND_URL = {json.dumps(backend_url)};\n")
PY

echo "Built frontend at $DIST_DIR"
