# Tests

Run all static and compilation checks from the monorepo root:

```bash
nix develop
uv lock                 # first run; creates uv.lock
uv sync --locked
./scripts/test-local.sh
```

The test script invokes Python through `uv run`; no global Python packages or
`pip install` into the Nix store are needed.

The static checker verifies manifest identity, dependency versions, template
entrypoints, thumbnail dimensions, YAML parsing, and relative/package imports.
The smoke tests compile both hand-maintained examples and both packaged template
entrypoints using isolated local package installation.

Add visual regression fixtures for line spacing, headings, figure and table
captions, multi-page tables, bibliography indentation, and page breaks before
considering the project ready for a stable release.
