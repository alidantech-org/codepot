"""Tests for template scanning."""

from __future__ import annotations

from tests.fixtures.templates import write_debug_templates
from src.emission.templates.scanner import scan_templates


def test_scan_templates_finds_jinja_and_raw_files(tmp_path) -> None:
    template_root = write_debug_templates(tmp_path)

    descriptors = scan_templates(template_root)
    paths = {descriptor.relative_path.as_posix() for descriptor in descriptors}

    assert "summary.txt.j2" in paths
    assert "{resource}/index.md.j2" in paths
    assert "{model}/[model.name.path.o].md.j2" in paths
    assert ".gitignore" in paths
    # paths.yaml should be excluded from scanning
    assert "paths.yaml" not in paths


def test_scan_templates_skips_underscore_folders(tmp_path) -> None:
    template_root = write_debug_templates(tmp_path)
    partial = template_root / "_partials" / "metadata.md.j2"
    partial.parent.mkdir(parents=True)
    partial.write_text("partial", encoding="utf-8")

    descriptors = scan_templates(template_root)
    paths = {descriptor.relative_path.as_posix() for descriptor in descriptors}

    assert "_partials/metadata.md.j2" not in paths
