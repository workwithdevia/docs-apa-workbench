# Typst Universe package layout

The monorepo uses descriptive folder names, but package registry destinations
are derived from the `name` and `version` fields in each `typst.toml`.

| Monorepo source | Registry destination |
|---|---|
| `packages/core/` | `packages/preview/nexum-apa-core/{version}/` |
| `packages/academic-paper/` | `packages/preview/nexum-apa-paper/{version}/` |
| `packages/laboratory-report/` | `packages/preview/nexum-apa-lab-report/{version}/` |

This monorepo is not the Typst package registry. Run
`scripts/prepare-universe-pr.sh` against a clone of `typst/packages` to copy a
selected package into its correct registry location. The script copies files;
it does not create Git submodules.
