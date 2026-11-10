# Changelog

## Unreleased

- Cite the DNA extraction rubric in the laboratory-methods example so its APA
  reference list is populated under Typst's default cited-works behavior.
- Add static validation that example and starter-template bibliography entries
  are cited, preventing an empty References page from passing unnoticed.
- Add `.gitlab-ci.yml` using the repository Nix flake and uv toolchain. The job
  compiles examples and preserves PDFs as GitLab artifacts.


This changelog tracks the monorepo scaffold. Individual Typst packages are
versioned independently in their own `typst.toml` manifests.

## Unreleased

- Organize the repository as one GitHub monorepo with three independently
  versioned Typst packages under `packages/core`, `packages/academic-paper`,
  and `packages/laboratory-report`.
- Add manifest-aware local installation and Typst Universe packaging scripts.
- Add static validation for manifests, dependencies, YAML, imports, and template
  thumbnail requirements.
- Add academic-paper and DNA-extraction examples.
