# Publishing to Typst Universe

APA Workbench is a GitHub monorepo; Typst Universe is a separate package
registry. A repository may contain several Typst packages. Each package has its
own `typst.toml`, package identifier, version, entrypoint, and (for templates)
`[template]` metadata.

## Package mapping

| Monorepo source folder | Manifest package name | Registry destination |
|---|---|---|
| `packages/core/` | `nexum-apa-core` | `packages/preview/nexum-apa-core/{version}/` |
| `packages/academic-paper/` | `nexum-apa-paper` | `packages/preview/nexum-apa-paper/{version}/` |
| `packages/laboratory-report/` | `nexum-apa-lab-report` | `packages/preview/nexum-apa-lab-report/{version}/` |

The source folder name is deliberately not required to equal the Typst package
name. All automation reads the canonical name and version from `typst.toml`.

## Dependency order

The two template packages import `@preview/nexum-apa-core:0.1.0`, so publish in
this order:

1. Submit `nexum-apa-core` and wait until it is accepted and downloadable.
2. Submit `nexum-apa-paper`.
3. Submit `nexum-apa-lab-report`.

The two templates may be submitted in either order after the core is available.

## Prepare a registry submission

Fork/clone `https://github.com/typst/packages`. From the APA Workbench root,
run one command per package:

```bash
./scripts/prepare-universe-pr.sh core /path/to/typst-packages
./scripts/prepare-universe-pr.sh academic-paper /path/to/typst-packages
./scripts/prepare-universe-pr.sh laboratory-report /path/to/typst-packages
```

The script reads `[package].name` and `[package].version` from the selected
manifest and copies the package files to the matching registry directory. It
refuses to overwrite an existing version folder and does not create Git
submodules.

Submit each package separately. Do not submit the template packages before the
core dependency is available in the registry.

## Pre-submission checklist

- [ ] Replace `YOUR NAME`, `YOUR_GITHUB_HANDLE`, and `YOUR_GITHUB_USER` in all
      three manifests.
- [ ] Confirm package names comply with the current Typst Universe naming rules.
- [ ] Ensure the GitHub repository URL in each manifest is correct.
- [ ] Run `uv sync --locked` using the committed `uv.lock`.
- [ ] Run `scripts/test-local.sh` using the minimum supported Typst compiler.
- [ ] Inspect all compiled PDFs, references, labels, page breaks, and fonts.
- [ ] Regenerate `thumbnail.png` from an actual compiled first page. The current
      thumbnails are design placeholders and must not be submitted as final.
- [ ] Check that each thumbnail is PNG or lossless WebP, has a longest edge of
      at least 1080 px, and is no larger than 3 MiB.
- [ ] Review the MIT license and all bundled assets for redistribution rights.
- [ ] Prepare and submit the core package first.
- [ ] Wait for acceptance, then submit both template packages.

## Naming

The `nexum-` prefix is provisional and must be checked against current naming
rules and existing packages. Typst Universe expects package names to be
non-canonical and, for templates, to begin with a unique non-descriptive part
followed by a descriptive part. The current identifiers are intended to follow
that pattern, but approval is determined by the registry maintainers.

## Official references

- [Package manifest format](https://github.com/typst/packages/blob/main/docs/manifest.md)
- [Package submission tips](https://github.com/typst/packages/blob/main/docs/tips.md)
- [Typst package registry](https://github.com/typst/packages)
