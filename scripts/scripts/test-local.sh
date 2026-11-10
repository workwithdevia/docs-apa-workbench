#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Bootstrap the repository's Python tooling through uv. On the first run,
# uv creates uv.lock and .venv; subsequent runs enforce the committed lock.
if [[ "${APA_WORKBENCH_UV_ACTIVE:-0}" != "1" ]]; then
  if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required. Enter the Nix development shell with: nix develop" >&2
    exit 1
  fi

  UV_LOCK_ARGS=()
  if [[ -f "$ROOT/uv.lock" ]]; then
    UV_LOCK_ARGS+=(--locked)
  fi

  exec env APA_WORKBENCH_UV_ACTIVE=1 \
    uv run "${UV_LOCK_ARGS[@]}" --project "$ROOT" \
    "$ROOT/scripts/test-local.sh" "$@"
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if ! command -v typst >/dev/null 2>&1; then
  echo "Typst CLI 0.15.0+ is required. See https://typst.app/docs/installation/" >&2
  exit 1
fi

VERSION="$(typst --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)"
python - "$VERSION" <<'PY'
import re
import sys

match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", sys.argv[1])
if match is None:
    raise SystemExit(f"Could not parse Typst version: {sys.argv[1]}")

version = tuple(map(int, match.groups()))
if version < (0, 15, 0):
    raise SystemExit(
        f"Typst 0.15.0 or later is required; found {sys.argv[1]}"
    )
PY

echo "Using Typst $VERSION"
python "$ROOT/scripts/check-static.py"

export XDG_DATA_HOME="$TMP/xdg"
export XDG_CACHE_HOME="$TMP/cache"
"$ROOT/scripts/install-local-packages.sh"

mkdir -p "$TMP/out"

# Compile the repository's complete examples.
typst compile --root "$ROOT" \
  "$ROOT/examples/academic-paper/main.typ" \
  "$TMP/out/academic-paper.pdf"

typst compile --root "$ROOT" \
  "$ROOT/examples/dna-extraction/main.typ" \
  "$TMP/out/dna-extraction.pdf"

# Compile the actual template-package starter files.
typst compile --root "$ROOT/packages/academic-paper/template" \
  "$ROOT/packages/academic-paper/template/main.typ" \
  "$TMP/out/academic-paper-template.pdf"

typst compile --root "$ROOT/packages/laboratory-report/template" \
  "$ROOT/packages/laboratory-report/template/main.typ" \
  "$TMP/out/laboratory-report-template.pdf"

echo "All four documents compiled successfully."
