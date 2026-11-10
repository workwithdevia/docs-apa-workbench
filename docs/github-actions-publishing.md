# Automatic publication to Typst Universe with GitHub Actions

This repository's public mirror is:

- Source: <https://github.com/workwithdevia/docs-apa-workbench>
- Typst registry fork: <https://github.com/workwithdevia/packages>
- Upstream registry: <https://github.com/typst/packages>

The workflow `.github/workflows/publish-typst-universe.yml` validates and compiles the repository before attempting publication.

## Events

- Every push to `main` runs validation and then the publisher.
- Pull requests run validation only; they never receive the publication token.
- A scheduled run every six hours retries packages whose dependencies have not yet been merged into `typst/packages`.
- `workflow_dispatch` allows a maintainer to retry from the Actions tab.

## One-time GitHub secret

In `workwithdevia/docs-apa-workbench`, open **Settings → Secrets and variables → Actions → New repository secret**.

Create:

- Name: `TYPST_PACKAGES_TOKEN`
- Value: a GitHub **personal access token (classic)** with the `public_repo` scope.

Why classic? GitHub currently documents a limitation in fine-grained personal access tokens for contributing to public repositories where the token owner is not a member. The classic `public_repo` scope permits the workflow to push a release branch to your public fork and open a pull request against `typst/packages`.

Treat this token like a password. Give it an expiration, do not print it in logs, and rotate it when needed. It is only exposed to the publication job, never to pull-request validation.

Create the token at:
<https://github.com/settings/tokens/new?scopes=public_repo>

## Required one-time manifest edits

The current mirror's three manifests still contain placeholder author and repository values. Replace them before the first publication:

- `packages/core/typst.toml`
- `packages/academic-paper/typst.toml`
- `packages/laboratory-report/typst.toml`

For each manifest, set a real author and the actual public mirror URL. For example:

```toml
authors = ["Your display name <@workwithdevia>"]
repository = "https://github.com/workwithdevia/docs-apa-workbench"
```

Use the public name you want displayed in Typst Universe. The publisher deliberately fails if it finds values such as `YOUR NAME`, `YOUR_GITHUB_HANDLE`, or `YOUR_GITHUB_USER`.

Do not change package names or versions just to enable the workflow. The package IDs and versions are read from each `typst.toml`.

## How publication is sequenced

The publisher processes packages in dependency order:

1. `packages/core` → `nexum-apa-core`.
2. `packages/academic-paper` → `nexum-apa-paper`.
3. `packages/laboratory-report` → `nexum-apa-lab-report`.

It checks the official registry's `main` branch before publishing a version. Existing versions are skipped. For a new version, it creates a branch in `workwithdevia/packages` and opens a pull request from that branch to `typst/packages:main`.

The two template packages import `@preview/nexum-apa-core:<version>`. Therefore, if that exact core version is not yet present in the official registry, template submissions are deferred. The scheduled workflow retries every six hours. Once the core PR is merged, the next scheduled or manually dispatched run submits the templates automatically.

If a PR already exists for the same package version, the automation updates its branch instead of creating a duplicate. It does not reopen a PR that was closed without merging. If a package version is already published, changes to that same version are skipped: increment the package's `version` in `typst.toml` for a new release, following SemVer.

## Trigger manually

After adding the secret and correcting the manifests, open:

<https://github.com/workwithdevia/docs-apa-workbench/actions/workflows/publish-typst-universe.yml>

Choose **Run workflow** on `main`.

The same workflow runs automatically on each push to `main`.

## Local dry run

The publisher can validate package metadata and dependencies without network access or credentials:

```bash
nix develop
python3 scripts/publish-to-typst-universe.py --dry-run
```

## What remains a human decision

Automation prepares and submits the pull requests. Typst's maintainers still review and decide whether to merge them. The workflow never merges its own pull requests into the official registry.
