# APA Workbench

Monorepo for developing and distributing three related Typst packages:

| Repository directory | Typst package ID | Responsibility | Typst category |
|---|---|---|---|
| `packages/core/` | `nexum-apa-core` | Shared APA composition engine, styles, and reusable components. | `components`, `layout`, `model` |
| `packages/academic-paper/` | `nexum-apa-paper` | Starter template for academic papers and research assignments. | `paper` |
| `packages/laboratory-report/` | `nexum-apa-lab-report` | Starter template for experimental and laboratory reports. | `report` |

**One GitHub repository, three independently versioned Typst packages.** The
folder names under `packages/` are organization labels. The public package IDs
are the `name` fields in each `typst.toml`; do not infer a package ID from its
monorepo directory name.

> **Development scaffold:** package IDs use the provisional `nexum-` prefix.
> Replace the placeholder authors and GitHub URL, verify name availability and
> current Typst Universe submission rules, and compile the examples before
> submitting anything for publication.

## Repository layout

```text
apa-workbench/
├── packages/
│   ├── core/                 # Typst package: nexum-apa-core
│   ├── academic-paper/       # Typst template package: nexum-apa-paper
│   └── laboratory-report/    # Typst template package: nexum-apa-lab-report
├── examples/
│   ├── academic-paper/
│   └── dna-extraction/
├── tests/
├── docs/
├── scripts/
└── .github/workflows/
```

The two template packages import the shared core using its published Typst
package identifier. The monorepo is the source of truth; the official Typst
package registry receives versioned copies of each package directory.

## Requirements

- Nix with flakes enabled (recommended development environment).
- Typst CLI 0.15.0 or later (CI currently tests 0.15.1).
- `uv` for Python tooling and dependency locking.
- Python 3.11 or later, provided by the Nix development shell.

Python development dependencies are declared in `pyproject.toml` and locked in
`uv.lock`. Do not install them into the Nix-managed Python with `pip`.

The repository does not bundle third-party fonts. A font name in `settings.yaml`
must be available in the compiling environment. In Typst.app, upload `.ttf` or
`.otf` font files to the project and verify the internal family name.

## Test the repository

```bash
nix develop
nix flake lock           # first run, then commit flake.lock
uv lock                  # first run, or after changing Python dependencies
uv sync --locked
chmod +x scripts/*.sh
./scripts/test-local.sh
```

`scripts/test-local.sh` also bootstraps the `uv` project environment when run
without a prior `uv sync`: it creates `uv.lock` on the first run, then enforces
the lock on subsequent runs. Commit both `flake.lock` and `uv.lock` so the Nix
and Python tooling versions are reproducible.

The test script runs its Python validation through `uv run`, creates an isolated
temporary `XDG_DATA_HOME`, installs all three packages under the local `preview`
package namespace using each manifest's
`name` and `version`, then compiles both complete examples. It does not need to
fetch these packages from Typst Universe.

To install the packages into your normal local Typst package directory:

```bash
./scripts/install-local-packages.sh
```

Then compile an example from the repository root:

```bash
typst compile --root . examples/dna-extraction/main.typ
```

## Create a project from a template

After publication and once the core dependency is available in Typst Universe:

```bash
typst init @preview/nexum-apa-paper:0.1.0
# or
typst init @preview/nexum-apa-lab-report:0.1.0
```

The generated project separates responsibilities:

- `metadata.yaml`: title, authors, affiliations, institution, course, instructor,
  date, laboratory information, and keywords.
- `settings.yaml`: page geometry, text/math/code fonts, paragraph layout, cover,
  and bibliography options.
- `content.typ`: explicit manifest mapping semantic section names to files.
- `sections/`: the author's section content.
- `references.bib`: bibliography entries.
- `figures/`: images and other user assets.

`main.typ` should only load these inputs and invoke the document template. The
library controls the document's composition order, page breaks, and styling.
Typst does not automatically enumerate a directory, so `content.typ` remains a
small explicit manifest rather than relying on unsupported folder discovery.

## Push this monorepo to GitHub

Create an empty public repository named `apa-workbench`, then run from this
folder:

```bash
git init
git add .
git commit -m "chore: initialize APA Workbench monorepo"
git branch -M main
git remote add origin git@github.com:YOUR_GITHUB_USER/apa-workbench.git
git push -u origin main
```

Replace `YOUR_GITHUB_USER` and the placeholder authors in the three manifests.
The `repository` field in each `typst.toml` should point to the actual repository.

## Publish packages to Typst Universe

The packages are independently versioned but developed in this single repo.
Publish in dependency order:

1. `packages/core/` → `nexum-apa-core`.
2. `packages/academic-paper/` → `nexum-apa-paper`.
3. `packages/laboratory-report/` → `nexum-apa-lab-report`.

Wait for the core package to be accepted and resolvable before submitting the
two templates, because their `lib.typ` files import `@preview/nexum-apa-core`.

Clone or fork `typst/packages`, then prepare one package at a time:

```bash
./scripts/prepare-universe-pr.sh core /path/to/typst-packages
./scripts/prepare-universe-pr.sh academic-paper /path/to/typst-packages
./scripts/prepare-universe-pr.sh laboratory-report /path/to/typst-packages
```

The script reads `name` and `version` from the selected package's `typst.toml`
and copies it to `packages/preview/{manifest-name}/{manifest-version}/` in the
registry clone. It copies files, not Git submodules. Review the result and
follow the current official submission checklist before opening each PR.

## GitLab CI

A GitLab pipeline is provided in `.gitlab-ci.yml`. It enters the same Nix flake
development shell used locally, runs the static and compilation checks, and
attaches the academic-paper and DNA-extraction PDFs as downloadable job
artifacts. See [docs/gitlab-ci.md](docs/gitlab-ci.md).

The DNA example includes a citation to `agudelo2026`. Typst only prints
bibliography entries that are cited when `full: false` (the APA-appropriate
default), so the in-text citation is required for that reference to appear.

## Validation status

The static checker validates package manifests, package IDs, template metadata,
thumbnail dimensions and file sizes, YAML files, relative imports/includes, and
internal package imports. The CI workflow additionally uses `uv` to sync the
locked Python tooling, installs Typst 0.15.1,
and compiles both examples. A local ZIP build is not itself proof of PDF
compilation; run `scripts/test-local.sh` before publishing.

## License

MIT. Each package includes its own `LICENSE` copy for registry distribution.
