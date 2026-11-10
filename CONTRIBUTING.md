# Contributing

Thanks for considering a contribution to APA Workbench.

## Before editing

1. Read `docs/architecture.md` and `docs/apa-conformance.md`.
2. Keep the public package identifiers in each `typst.toml` synchronized with
   imports in the dependent template packages and examples.
3. Keep the three package folders (`core`, `academic-paper`, and
   `laboratory-report`) separate; shared formatting belongs in `core`.

## Validation

```bash
nix develop
nix flake lock            # first run; commit flake.lock
uv lock                   # first run; commit uv.lock
uv sync --locked
uv run --locked python scripts/check-static.py
scripts/test-local.sh
```

Do not use `pip install` against the Nix-managed interpreter. Add or update
Python development dependencies with `uv add --group dev <package>`, then run
`uv lock` and commit the updated `uv.lock`.

Do not report PDF or APA-conformance validation unless the relevant Typst
compilation and visual inspection have actually been performed.

## Versioning

Use semantic versioning for each package independently. If the core API changes,
consider compatibility with both template packages and update their imported
core version before publishing the template releases.

## Pull requests

Include a short problem statement, implementation summary, test results, and
screenshots or PDFs when a change affects layout. Avoid unrelated formatting or
scientific-content rewrites in document examples.
