# Apply this publication-automation patch

This ZIP is a patch for the existing public repository:

<https://github.com/workwithdevia/docs-apa-workbench>

Extract its contents at the repository root, preserving the paths. It adds:

- `.github/workflows/publish-typst-universe.yml`
- `scripts/publish-to-typst-universe.py`
- `docs/github-actions-publishing.md`

Then:

1. Replace placeholder `authors` and `repository` values in the three `packages/*/typst.toml` manifests.
2. Add the repository Actions secret `TYPST_PACKAGES_TOKEN` (classic GitHub PAT with `public_repo` scope).
3. Commit and push the files to `main` of `workwithdevia/docs-apa-workbench`.
4. Check the Actions run. The first run opens the core package PR if its version is not published yet. Templates are submitted after the exact core dependency is merged; the scheduled run retries automatically every six hours.

No files in the existing GitLab pipeline are replaced.
