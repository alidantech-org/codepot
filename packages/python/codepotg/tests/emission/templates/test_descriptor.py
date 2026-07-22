"""Tests for template descriptor parsing with folder recipe paths."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.emission.templates.descriptor import describe_template


def test_descriptor_extracts_folder_token():
    root = Path("/templates")
    descriptor = describe_template(root, Path("{model}/[model.name.path.o].txt.j2"))

    assert len(descriptor.folders) == 1
    assert descriptor.folders[0].expression == "model"


def test_descriptor_excludes_folder_from_output_parts():
    root = Path("/templates")
    descriptor = describe_template(root, Path("{model}/[model.name.path.o].txt.j2"))

    assert descriptor.output_parts == ("[model.name.path.o].txt.j2",)
    assert "{model}" not in descriptor.output_parts


def test_descriptor_allows_folder_in_middle():
    root = Path("/templates")
    descriptor = describe_template(root, Path("debug/{model}/[model.name.path.o].txt.j2"))

    assert tuple(token.expression for token in descriptor.folders) == ("model",)
    assert descriptor.output_parts == ("debug", "[model.name.path.o].txt.j2")


def test_descriptor_rejects_multiple_folder_tokens():
    root = Path("/templates")

    with pytest.raises(ValueError, match="only one folder recipe token"):
        describe_template(root, Path("{resource}/{model}/[model.name.path.o].txt.j2"))


def test_descriptor_no_folder_global():
    root = Path("/templates")
    descriptor = describe_template(root, Path("README.md.j2"))

    assert len(descriptor.folders) == 0
    assert descriptor.output_parts == ("README.md.j2",)


def test_descriptor_identifies_jinja_template():
    root = Path("/templates")
    descriptor = describe_template(root, Path("{model}/[model.name.path.o].txt.j2"))

    assert descriptor.is_template is True


def test_descriptor_identifies_raw_file():
    root = Path("/templates")
    descriptor = describe_template(root, Path(".gitignore"))

    assert descriptor.is_template is False


def test_descriptor_parses_segments():
    root = Path("/templates")
    descriptor = describe_template(root, Path("{model}/[model.name.path.o].txt.j2"))

    assert len(descriptor.segments) == 2
    assert descriptor.segments[0].is_folder is True
    assert descriptor.segments[1].is_dynamic is True


def test_descriptor_escaped_folder_segment_not_folder():
    root = Path("/templates")
    descriptor = describe_template(root, Path("docs/{{not-folder}}/page.txt.j2"))

    assert len(descriptor.folders) == 0
    assert descriptor.output_parts == ("docs", "{{not-folder}}", "page.txt.j2")


def test_descriptor_dynamic_segment_not_folder():
    root = Path("/templates")
    descriptor = describe_template(root, Path("lib/[version]/file.txt.j2"))

    assert len(descriptor.folders) == 0
    assert descriptor.output_parts == ("lib", "[version]", "file.txt.j2")
