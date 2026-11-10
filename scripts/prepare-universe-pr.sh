#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 {core|academic-paper|laboratory-report} /path/to/typst-packages-clone" >&2
  exit 2
fi

KIND="$1"
TARGET="$(cd -- "$2" && pwd)"

case "$KIND" in
  core) FOLDER="core" ;;
  academic-paper) FOLDER="academic-paper" ;;
  laboratory-report) FOLDER="laboratory-report" ;;
  *) echo "Unknown package: $KIND" >&2; exit 2 ;;
esac

SOURCE="$ROOT/packages/$FOLDER"
MANIFEST="$SOURCE/typst.toml"
if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing package manifest: $MANIFEST" >&2
  exit 1
fi

read_field() {
  python3 - "$MANIFEST" "$1" <<'PY'
import sys
import tomllib
from pathlib import Path
manifest = Path(sys.argv[1])
field = sys.argv[2]
print(tomllib.loads(manifest.read_text(encoding="utf-8"))["package"][field])
PY
}

NAME="$(read_field name)"
VERSION="$(read_field version)"
DEST="$TARGET/packages/preview/$NAME/$VERSION"

if [[ "$KIND" != "core" ]]; then
  echo "Reminder: submit nexum-apa-core and wait for acceptance before dependent packages." >&2
fi

if [[ -e "$DEST" ]]; then
  echo "Destination already exists: $DEST" >&2
  echo "Remove it explicitly before preparing an overwrite." >&2
  exit 1
fi

mkdir -p "$DEST"
cp -a "$SOURCE/." "$DEST/"
rm -rf "$DEST/.git"

echo "Prepared $NAME:$VERSION at $DEST"
echo "Review README, manifest authors/repository, package size, licensing and template thumbnail before opening the PR."
