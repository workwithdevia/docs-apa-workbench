#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
PACKAGES_DIR="$DATA_HOME/typst/packages/preview"

read_manifest_field() {
  local manifest="$1"
  local field="$2"
  python3 - "$manifest" "$field" <<'PY'
import sys
import tomllib
from pathlib import Path
manifest = Path(sys.argv[1])
field = sys.argv[2]
data = tomllib.loads(manifest.read_text(encoding="utf-8"))
value = data["package"][field]
print(value)
PY
}

install_one() {
  local folder="$1"
  local source="$ROOT/packages/$folder"
  local manifest="$source/typst.toml"
  if [[ ! -f "$manifest" ]]; then
    echo "Missing package manifest: $manifest" >&2
    exit 1
  fi

  local name version
  name="$(read_manifest_field "$manifest" name)"
  version="$(read_manifest_field "$manifest" version)"

  mkdir -p "$PACKAGES_DIR/$name"
  rm -rf "$PACKAGES_DIR/$name/$version"
  mkdir -p "$PACKAGES_DIR/$name/$version"
  cp -a "$source/." "$PACKAGES_DIR/$name/$version/"
  echo "Installed @preview/$name:$version from packages/$folder"
}

# Install the dependency before the two templates.
install_one core
install_one academic-paper
install_one laboratory-report
