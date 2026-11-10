# Development

## Python tooling with uv

Python dependencies are declared in `pyproject.toml` under the `dev`
dependency group. `uv.lock` pins their resolved versions.

```bash
nix develop
nix flake lock            # first run; commit flake.lock
uv lock                   # first run; commit uv.lock
uv sync --locked
uv run --locked python scripts/check-static.py
```

The Nix shell provides `uv`, Python, Typst, and the system libraries/fonts used
by the examples. It sets `UV_PYTHON` to the Nix-provided interpreter and disables
uv-managed Python downloads, avoiding generic Linux Python builds on NixOS.

Use `uv add --group dev <package>` to add a development dependency. Then run
`uv lock`, review `pyproject.toml` and `uv.lock`, and commit both files.
Do not use `python -m pip install` against the Nix-managed interpreter.

## Local package resolution

`scripts/test-local.sh` creates a temporary `XDG_DATA_HOME` and installs each
package under `typst/packages/preview/{manifest-name}/{manifest-version}`.
The package name and version are read from `typst.toml`, not inferred from the
monorepo directory name. This lets the examples resolve package imports without
fetching the not-yet-published packages from Typst Universe.

## Updating versions

1. Increment the changed package's `version` in its `typst.toml`.
2. If the core version changes, update the core package import in both template
   packages' `lib.typ` files and in their README usage examples.
3. Update any template self-imports and examples if a template package version
   changes.
4. Run `uv run --locked python scripts/check-static.py` and
   `scripts/test-local.sh`.
5. Prepare and submit the core update before dependent template updates.

## Tests

The smoke-test script compiles both complete examples. The static checker
validates package identity, manifests, template paths, thumbnails, YAML, and
relative imports. Add targeted visual and regression fixtures for heading
levels, bibliography, captions, page breaks, long tables, and font fallback as
the implementation matures.
