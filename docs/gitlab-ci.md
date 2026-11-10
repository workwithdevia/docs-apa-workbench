# GitLab CI

APA Workbench includes a GitLab pipeline in `.gitlab-ci.yml`. It uses the official
`nixos/nix` container and the repository flake so CI runs with the same Nix, uv,
Python, fonts, and Typst toolchain as local development.

## Pipeline behavior

On branch pushes, merge requests, and tags, the `validate-and-build` job:

1. Enters `nix develop` with flakes enabled.
2. Runs `scripts/test-local.sh`, which validates manifests, YAML, imports,
   cited bibliography entries, installs the three local packages in an isolated
   Typst package directory, and compiles the four example/template documents.
3. Installs the packages into a temporary CI data directory and builds the
   academic-paper and DNA-extraction example PDFs.
4. Publishes both PDFs as GitLab job artifacts for one week.

## Run locally

```bash
nix develop --command ./scripts/test-local.sh
```

To produce PDFs locally:

```bash
export XDG_DATA_HOME="$PWD/.ci/xdg"
./scripts/install-local-packages.sh
mkdir -p build
typst compile --root "$PWD" examples/academic-paper/main.typ build/academic-paper.pdf
typst compile --root "$PWD" examples/dna-extraction/main.typ build/dna-extraction.pdf
```

## Runner requirements

The included pipeline expects a GitLab Runner using the Docker executor (or a
compatible executor that supports job images). It uses `nixos/nix:2.35.5`.
The container needs outbound access to fetch Nix flake inputs and Typst package
files. Nix sandboxing is disabled by default in the upstream Docker image; this
pipeline does not require privileged mode.

For reproducible CI, commit `flake.lock` and `uv.lock` to the repository. The
uv cache is stored under `.cache/uv/`; the virtual environment is not cached.
