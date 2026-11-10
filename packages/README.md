# Package index

The directory names here are repository organization labels. The public Typst
package identifiers are defined by each `typst.toml` manifest.

| Repository directory | Typst package identifier | Purpose | Publish order |
|---|---|---|---:|
| [`core/`](core/README.md) | `nexum-apa-core` | Shared APA composition and styling engine. | 1 |
| [`academic-paper/`](academic-paper/README.md) | `nexum-apa-paper` | Academic paper starter template. | 2 |
| [`laboratory-report/`](laboratory-report/README.md) | `nexum-apa-lab-report` | Laboratory report starter template. | 2 |

Do not rename a package directory to change its Typst identity. Change the
`[package].name` field and all imports together, then re-check Typst Universe's
naming rules before publishing.
