#!/usr/bin/env python3
"""Publish versioned APA Workbench packages to the official Typst registry.

The script is intentionally idempotent:
- Existing published package versions are skipped.
- Existing open PR branches are force-updated instead of duplicated.
- Template packages are held until their exact apa-core dependency is published.
- Closed, unmerged PRs are not reopened automatically.

Required environment variables for publishing:
    TYPST_PACKAGES_TOKEN  Classic GitHub PAT with the public_repo scope.

Optional environment variables:
    TYPST_PACKAGES_FORK       Fork owner/repo (default: workwithdevia/packages)
    TYPST_SOURCE_REPOSITORY   Source repo URL (default: current public mirror)
    GITHUB_SHA                Source commit, supplied by GitHub Actions.

Use --dry-run to validate manifests and print the plan without network access.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "typst/packages"
DEFAULT_FORK = "workwithdevia/packages"
DEFAULT_SOURCE_REPOSITORY = "https://github.com/workwithdevia/docs-apa-workbench"
API_BASE = "https://api.github.com"
API_VERSION = "2022-11-28"

PACKAGES = (
    ("core", "nexum-apa-core"),
    ("academic-paper", "nexum-apa-paper"),
    ("laboratory-report", "nexum-apa-lab-report"),
)

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
CORE_IMPORT_RE = re.compile(r"@preview/nexum-apa-core:(\d+\.\d+\.\d+)")
PLACEHOLDER_RE = re.compile(
    r"YOUR[_ ]NAME|YOUR[_ ]GITHUB|YOUR[_ ]USER|TODO|CHANGE[_ ]ME|PLACEHOLDER",
    re.IGNORECASE,
)


class PublishError(RuntimeError):
    """An actionable publication error."""


def log(message: str) -> None:
    print(message, flush=True)


def run_git(args: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        raise PublishError(
            f"Git command failed: git {' '.join(args)}\n{result.stdout.strip()}"
        )
    return result.stdout.strip()


def api_request(
    token: str,
    method: str,
    endpoint: str,
    payload: dict[str, Any] | None = None,
    *,
    allow_404: bool = False,
) -> Any:
    url = f"{API_BASE}{endpoint}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "apa-workbench-typst-publisher",
            **({"Content-Type": "application/json"} if body is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        if error.code == 404 and allow_404:
            return None
        raise PublishError(
            f"GitHub API {method} {endpoint} returned HTTP {error.code}: {details}"
        ) from error
    except urllib.error.URLError as error:
        raise PublishError(f"Cannot reach GitHub API: {error}") from error


def contents_path_exists(token: str, package_name: str, version: str) -> bool:
    path = f"packages/preview/{package_name}/{version}"
    encoded = urllib.parse.quote(path, safe="/")
    result = api_request(
        token,
        "GET",
        f"/repos/{UPSTREAM}/contents/{encoded}?ref=main",
        allow_404=True,
    )
    return result is not None


def read_manifest(folder: str, expected_name: str, source_repository: str) -> dict[str, Any]:
    package_dir = ROOT / "packages" / folder
    manifest_path = package_dir / "typst.toml"
    if not manifest_path.is_file():
        raise PublishError(f"Missing package manifest: {manifest_path.relative_to(ROOT)}")

    try:
        manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise PublishError(f"Invalid TOML in {manifest_path.relative_to(ROOT)}: {error}") from error

    package = manifest.get("package", {})
    name = package.get("name")
    version = package.get("version")
    if name != expected_name:
        raise PublishError(
            f"{folder}/typst.toml: expected package name {expected_name!r}, got {name!r}"
        )
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        raise PublishError(f"{name}: version must be a full SemVer triple, got {version!r}")

    for field in ("authors", "license", "description"):
        if not package.get(field):
            raise PublishError(f"{name}: required Typst Universe manifest field {field!r} is missing")

    authors = package.get("authors", [])
    author_text = " ".join(authors) if isinstance(authors, list) else str(authors)
    if PLACEHOLDER_RE.search(author_text):
        raise PublishError(
            f"{name}: replace the placeholder author in {folder}/typst.toml "
            "before publishing (for example: 'Your Name <@workwithdevia>')."
        )

    repository = package.get("repository", "")
    if PLACEHOLDER_RE.search(repository) or repository != source_repository:
        raise PublishError(
            f"{name}: set repository = {source_repository!r} in {folder}/typst.toml "
            f"(currently {repository!r})."
        )

    if not (package_dir / package.get("entrypoint", "lib.typ")).is_file():
        raise PublishError(f"{name}: package entrypoint does not exist")
    for required in ("README.md", "LICENSE"):
        if not (package_dir / required).is_file():
            raise PublishError(f"{name}: required file {folder}/{required} is missing")

    if folder != "core":
        template = manifest.get("template")
        if not isinstance(template, dict):
            raise PublishError(f"{name}: template package is missing [template] in typst.toml")
        template_root = package_dir / template.get("path", "template")
        if not (template_root / template.get("entrypoint", "main.typ")).is_file():
            raise PublishError(f"{name}: template entrypoint is missing")
        if not template.get("thumbnail") or not (package_dir / template["thumbnail"]).is_file():
            raise PublishError(f"{name}: template thumbnail is missing")
        if not package.get("categories"):
            raise PublishError(f"{name}: template package needs at least one category")

    return {
        "folder": folder,
        "name": name,
        "version": version,
        "directory": package_dir,
        "manifest": manifest,
    }


def required_core_version(package_dir: Path) -> str:
    versions: set[str] = set()
    for path in package_dir.rglob("*.typ"):
        source = path.read_text(encoding="utf-8")
        versions.update(CORE_IMPORT_RE.findall(source))
    if len(versions) != 1:
        raise PublishError(
            f"{package_dir.name}: expected exactly one @preview/nexum-apa-core version, "
            f"found {sorted(versions)}"
        )
    return next(iter(versions))


def check_fork(token: str, fork: str) -> str:
    parts = fork.split("/")
    if len(parts) != 2 or not all(parts):
        raise PublishError("TYPST_PACKAGES_FORK must have the form owner/repo")
    owner, repo = parts
    data = api_request(token, "GET", f"/repos/{owner}/{repo}")
    parent = data.get("parent", {}) or {}
    if not data.get("fork") or parent.get("full_name", "").lower() != UPSTREAM:
        raise PublishError(
            f"{fork} is not a GitHub fork of {UPSTREAM}. "
            "Create/use the fork of typst/packages before running publication."
        )
    return owner


def list_matching_prs(token: str, owner: str, branch: str) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "state": "all",
            "head": f"{owner}:{branch}",
            "base": "main",
            "per_page": "100",
        }
    )
    result = api_request(token, "GET", f"/repos/{UPSTREAM}/pulls?{query}")
    return result if isinstance(result, list) else []


def prepare_and_push_package(
    *,
    registry: Path,
    package: dict[str, Any],
    fork: str,
    token: str,
    askpass: Path,
    git_env: dict[str, str],
) -> str:
    name = package["name"]
    version = package["version"]
    branch = f"automation/apa-workbench/{name}/{version}"
    destination_rel = Path("packages") / "preview" / name / version
    destination = registry / destination_rel

    # Every publication branch starts from the current official registry main.
    run_git(["checkout", "--force", "-B", branch, "origin/main"], cwd=registry, env=git_env)
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    ignored = shutil.ignore_patterns(
        ".git", ".direnv", ".venv", "__pycache__", "*.pyc",
        ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache", "build",
    )
    shutil.copytree(package["directory"], destination, ignore=ignored)

    run_git(["add", "--all", str(destination_rel)], cwd=registry, env=git_env)
    staged = run_git(["diff", "--cached", "--name-only"], cwd=registry, env=git_env)
    if not staged:
        raise PublishError(f"No files staged for {name}:{version}; refusing to publish an empty PR")

    run_git(
        [
            "-c", "user.name=APA Workbench Publisher",
            "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit", "-m", f"Add {name} {version}",
        ],
        cwd=registry,
        env=git_env,
    )

    run_git(
        ["push", "--force", "fork", f"HEAD:refs/heads/{branch}"],
        cwd=registry,
        env=git_env,
    )
    return branch


def ensure_pull_request(
    token: str,
    owner: str,
    branch: str,
    package: dict[str, Any],
    dependency_version: str | None,
) -> str:
    name = package["name"]
    version = package["version"]
    existing = list_matching_prs(token, owner, branch)
    if existing:
        # There should normally be one PR per dedicated publication branch.
        pr = existing[0]
        if pr.get("merged_at"):
            raise PublishError(
                f"PR {pr.get('html_url')} is already merged, but {name}:{version} "
                "is not visible in the upstream package registry. Check the registry manually."
            )
        if pr.get("state") == "closed":
            log(
                f"NOTICE: {name}:{version} has a closed, unmerged PR "
                f"({pr.get('html_url')}). It was not reopened automatically."
            )
            return pr.get("html_url", "closed PR")
        log(f"Updated existing PR for {name}:{version}: {pr.get('html_url')}")
        return pr.get("html_url", "existing PR")

    body_lines = [
        f"## Package submission: `{name}` `{version}`",
        "",
        "This pull request publishes a versioned APA Workbench package to Typst Universe.",
        "",
        f"- Source repository: https://github.com/workwithdevia/docs-apa-workbench",
        f"- Source commit: `{os.getenv('GITHUB_SHA', 'local')}`",
        "- Package files are copied into the registry; no Git submodules are used.",
    ]
    if dependency_version:
        body_lines.extend(
            [
                "",
                f"- Dependency: `@preview/nexum-apa-core:{dependency_version}` "
                "is already present in the official registry.",
            ]
        )
    body_lines.extend(
        [
            "",
            "The source project's CI compiles the academic-paper and DNA-extraction examples "
            "with Typst 0.15.1 before this PR is opened.",
        ]
    )

    created = api_request(
        token,
        "POST",
        f"/repos/{UPSTREAM}/pulls",
        {
            "title": f"Add {name} {version}",
            "head": f"{owner}:{branch}",
            "base": "main",
            "body": "\n".join(body_lines),
            "maintainer_can_modify": True,
        },
    )
    url = created.get("html_url", "PR created")
    log(f"Created PR for {name}:{version}: {url}")
    return url


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate package metadata and dependencies without contacting GitHub.",
    )
    args = parser.parse_args()

    fork = os.getenv("TYPST_PACKAGES_FORK", DEFAULT_FORK)
    source_repository = os.getenv("TYPST_SOURCE_REPOSITORY", DEFAULT_SOURCE_REPOSITORY)

    packages = [read_manifest(folder, expected, source_repository) for folder, expected in PACKAGES]
    core_version = packages[0]["version"]
    # Fail early if template packages refer to a different core version.
    for package in packages[1:]:
        dependency = required_core_version(package["directory"])
        if dependency != core_version:
            raise PublishError(
                f"{package['name']} imports nexum-apa-core:{dependency}, "
                f"but packages/core/typst.toml declares {core_version}."
            )
        package["core_dependency"] = dependency

    log("Validated package manifests:")
    for package in packages:
        suffix = (
            f" (requires nexum-apa-core:{package['core_dependency']})"
            if package.get("core_dependency")
            else ""
        )
        log(f"  - {package['name']}:{package['version']}{suffix}")

    if args.dry_run:
        log("Dry run complete; no GitHub API calls or pushes were made.")
        return 0

    token = os.getenv("TYPST_PACKAGES_TOKEN", "")
    if not token:
        raise PublishError(
            "Missing TYPST_PACKAGES_TOKEN. Add a GitHub Actions secret containing a "
            "classic personal access token with the public_repo scope."
        )

    owner = check_fork(token, fork)
    log(f"Using Typst package fork: {fork}")

    with tempfile.TemporaryDirectory(prefix="apa-workbench-typst-publish-") as temporary:
        temp_root = Path(temporary)
        registry = temp_root / "typst-packages"
        askpass = temp_root / "git-askpass.sh"
        askpass.write_text(
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            "  *Username*) printf '%s\\n' 'x-access-token' ;;\n"
            "  *) printf '%s\\n' \"$TYPST_PACKAGES_TOKEN\" ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        askpass.chmod(0o700)
        git_env = os.environ.copy()
        git_env.update(
            {
                "GIT_ASKPASS": str(askpass),
                "GIT_TERMINAL_PROMPT": "0",
                "TYPST_PACKAGES_TOKEN": token,
            }
        )

        log(f"Cloning {UPSTREAM} (sparse checkout)...")
        run_git(
            [
                "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                f"https://github.com/{UPSTREAM}.git", str(registry),
            ],
            cwd=ROOT,
            env=git_env,
        )
        sparse_paths = [
            f"packages/preview/{package['name']}" for package in packages
        ]
        run_git(["sparse-checkout", "set", *sparse_paths], cwd=registry, env=git_env)
        run_git(["remote", "add", "fork", f"https://github.com/{fork}.git"], cwd=registry, env=git_env)
        run_git(["config", "user.name", "APA Workbench Publisher"], cwd=registry, env=git_env)
        run_git(
            ["config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
            cwd=registry,
            env=git_env,
        )

        # The order matters: the two templates are submitted only after the exact
        # core version they import has landed in typst/packages main.
        core_is_published = contents_path_exists(token, packages[0]["name"], core_version)

        for index, package in enumerate(packages):
            name = package["name"]
            version = package["version"]

            if contents_path_exists(token, name, version):
                log(f"Already published; skipping {name}:{version}")
                if index == 0:
                    core_is_published = True
                continue

            dependency_version = package.get("core_dependency")
            if dependency_version and not contents_path_exists(
                token, "nexum-apa-core", dependency_version
            ):
                log(
                    f"WAITING: {name}:{version} requires "
                    f"@preview/nexum-apa-core:{dependency_version}, which is not merged "
                    "into typst/packages main yet. It will be retried by the scheduled workflow."
                )
                continue

            branch = prepare_and_push_package(
                registry=registry,
                package=package,
                fork=fork,
                token=token,
                askpass=askpass,
                git_env=git_env,
            )
            ensure_pull_request(
                token,
                owner,
                branch,
                package,
                dependency_version,
            )

    log("Typst Universe publication pass completed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PublishError as error:
        print(f"::error::{error}", file=sys.stderr)
        raise SystemExit(1)
