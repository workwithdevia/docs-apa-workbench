## Publish to Typst Universe

Pushes to `main` trigger the GitHub Actions workflow that validates the examples and
submits any unpublished package versions to the `workwithdevia/packages` fork of
`typst/packages`. The workflow processes `nexum-apa-core` first and defers the two
templates until their exact core dependency has been merged into the official
registry. A scheduled run retries the deferred templates every six hours.

See [docs/github-actions-publishing.md](docs/github-actions-publishing.md) for the
one-time `TYPST_PACKAGES_TOKEN` setup, required manifest metadata, and publication
sequence.
