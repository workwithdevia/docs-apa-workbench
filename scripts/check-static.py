from __future__ import annotations

from pathlib import Path
import re
import struct
import tomllib

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PACKAGES = {
    "core": "nexum-apa-core",
    "academic-paper": "nexum-apa-paper",
    "laboratory-report": "nexum-apa-lab-report",
}

manifests: dict[str, tuple[str, str, dict]] = {}
for folder, expected_name in EXPECTED_PACKAGES.items():
    manifest = ROOT / "packages" / folder / "typst.toml"
    assert manifest.is_file(), f"Missing manifest: {manifest}"
    data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    package = data["package"]
    name = package["name"]
    version = package["version"]
    assert name == expected_name, f"{folder}: expected package ID {expected_name}, found {name}"
    assert re.fullmatch(r"\d+\.\d+\.\d+", version), f"Invalid SemVer: {name} {version}"
    assert package["license"] == "MIT"
    assert package.get("authors"), f"No authors in {manifest}"
    assert (manifest.parent / package["entrypoint"]).is_file(), f"Missing entrypoint for {name}"
    assert (manifest.parent / "README.md").is_file(), f"Missing README for {name}"
    assert (manifest.parent / "LICENSE").is_file(), f"Missing LICENSE for {name}"

    if "template" in data:
        template = data["template"]
        template_root = manifest.parent / template["path"]
        assert (template_root / template["entrypoint"]).is_file(), f"Missing template entrypoint for {name}"
        assert template.get("thumbnail"), f"Missing template thumbnail field for {name}"
        thumbnail = manifest.parent / template["thumbnail"]
        assert thumbnail.is_file(), f"Missing thumbnail: {thumbnail}"
        assert thumbnail.stat().st_size <= 3 * 1024 * 1024, f"Thumbnail exceeds 3 MiB: {thumbnail}"
        png = thumbnail.read_bytes()
        assert png[:8] == b"\x89PNG\r\n\x1a\n", f"Thumbnail must be PNG: {thumbnail}"
        width, height = struct.unpack(">II", png[16:24])
        assert max(width, height) >= 1080, f"Thumbnail long edge is below 1080px: {thumbnail} ({width}x{height})"
        assert package.get("categories"), f"Template package {name} needs at least one category"
        assert len(package["categories"]) <= 3, f"Too many categories in {name}"

    manifests[name] = (folder, version, data)

assert len(manifests) == 3, f"Expected 3 packages, found {len(manifests)}"

# Template packages depend on the shared core at the exact core version.
core_version = manifests["nexum-apa-core"][1]
for template_name in ("nexum-apa-paper", "nexum-apa-lab-report"):
    folder = manifests[template_name][0]
    lib_text = (ROOT / "packages" / folder / "lib.typ").read_text(encoding="utf-8")
    expected_import = f'@preview/nexum-apa-core:{core_version}'
    assert expected_import in lib_text, f"{template_name} must import {expected_import}"

# Validate YAML in all template projects and examples.
for base in [ROOT / "packages", ROOT / "examples"]:
    for yaml_file in list(base.rglob("*.yaml")) + list(base.rglob("*.yml")):
        parsed = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        assert parsed is None or isinstance(parsed, (dict, list)), f"Unexpected YAML root in {yaml_file}"

# Resolve quoted relative Typst imports/includes inside packages and examples.
for base in [ROOT / "packages", ROOT / "examples"]:
    for typ_file in base.rglob("*.typ"):
        text = typ_file.read_text(encoding="utf-8")
        for match in re.finditer(r'(?:#import|#include)\s+"([^"@][^"]*)"', text):
            rel = match.group(1)
            target = (typ_file.parent / rel).resolve()
            assert target.exists(), f"Missing relative path {rel} in {typ_file.relative_to(ROOT)}"

# Validate package-style imports against this monorepo's package manifests.
for base in [ROOT / "packages", ROOT / "examples"]:
    for typ_file in base.rglob("*.typ"):
        text = typ_file.read_text(encoding="utf-8")
        for name, version in re.findall(r'@preview/([a-z0-9-]+):(\d+\.\d+\.\d+)', text):
            assert name in manifests, f"Unknown package import @{name} in {typ_file.relative_to(ROOT)}"
            assert manifests[name][1] == version, (
                f"Version mismatch for @{name} in {typ_file.relative_to(ROOT)}: "
                f"import uses {version}, manifest uses {manifests[name][1]}"
            )

# Ensure package template entrypoints use package imports, not relative imports
# to sibling monorepo directories. This mirrors the Universe requirement.
for folder, package_name in (("academic-paper", "nexum-apa-paper"), ("laboratory-report", "nexum-apa-lab-report")):
    main_file = ROOT / "packages" / folder / "template" / "main.typ"
    text = main_file.read_text(encoding="utf-8")
    assert f'@preview/{package_name}:' in text, f"Template must self-import {package_name}"

# Confirm the exact root layout expected by the monorepo design.
for path in ["packages/core", "packages/academic-paper", "packages/laboratory-report", "examples/academic-paper", "examples/dna-extraction", "tests", "docs", "scripts", ".github/workflows"]:
    assert (ROOT / path).is_dir(), f"Missing expected directory: {path}"


# Bibliographies default to cited works only (Typst's `full: false`).
# Ensure every sample document has at least one citation matching its .bib keys,
# otherwise its rendered References heading would be empty.
def assert_bibliography_is_cited(project: Path) -> None:
    bib_path = project / "references.bib"
    assert bib_path.is_file(), f"Missing bibliography: {bib_path}"
    bib_text = bib_path.read_text(encoding="utf-8")
    keys = re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib_text)
    assert keys, f"No bibliography entries found in {bib_path}"

    typ_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in project.rglob("*.typ")
        if path.name not in {"main.typ"}
    )
    cited = [key for key in keys if re.search(rf"(?<![A-Za-z0-9_-])@{re.escape(key)}(?![A-Za-z0-9_-])", typ_sources)]
    assert cited, (
        f"Bibliography {bib_path.relative_to(ROOT)} has entries but none are cited. "
        "With Typst's default full: false, the references list will be empty."
    )


for sample in [
    ROOT / "examples/academic-paper",
    ROOT / "examples/dna-extraction",
    ROOT / "packages/academic-paper/template",
    ROOT / "packages/laboratory-report/template",
]:
    assert_bibliography_is_cited(sample)

print("Static checks passed: 3 manifests, package IDs, dependencies, templates, thumbnails, YAML, and imports and cited bibliographies.")
