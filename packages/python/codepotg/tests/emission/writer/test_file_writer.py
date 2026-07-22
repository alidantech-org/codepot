"""Tests for changed-aware file writing."""

from __future__ import annotations

from pathlib import Path

from src.emission.writer.file_writer import write_text_if_changed


def test_write_text_if_changed_creates_file(tmp_path: Path) -> None:
    path = tmp_path / "hello.txt"

    result = write_text_if_changed(path, "hello")

    assert path.read_text(encoding="utf-8") == "hello\n"
    assert result.created == (path,)


def test_write_text_if_changed_leaves_unchanged_file(tmp_path: Path) -> None:
    path = tmp_path / "hello.txt"
    path.write_text("hello\n", encoding="utf-8")

    result = write_text_if_changed(path, "hello")

    assert result.unchanged == (path,)


def test_write_text_if_changed_updates_changed_file(tmp_path: Path) -> None:
    path = tmp_path / "hello.txt"
    path.write_text("old\n", encoding="utf-8")

    result = write_text_if_changed(path, "new")

    assert path.read_text(encoding="utf-8") == "new\n"
    assert result.updated == (path,)


def test_layout_insensitive_ignores_whitespace_outside_strings(tmp_path: Path) -> None:
    path = tmp_path / "code.txt"
    path.write_text('print("hello world")\n', encoding="utf-8")

    # Same content with different spacing outside string
    result = write_text_if_changed(path, 'print(  "hello world"  )', compare_mode="layout_insensitive")

    assert result.unchanged == (path,)


def test_layout_insensitive_detects_string_content_changes(tmp_path: Path) -> None:
    path = tmp_path / "code.txt"
    path.write_text('print("hello world")\n', encoding="utf-8")

    # Different string content
    result = write_text_if_changed(path, 'print("helloworld")', compare_mode="layout_insensitive")

    assert result.updated == (path,)


def test_layout_insensitive_detects_code_changes(tmp_path: Path) -> None:
    path = tmp_path / "code.txt"
    path.write_text('print("hello")\n', encoding="utf-8")

    # Different code
    result = write_text_if_changed(path, 'console.log("hello")', compare_mode="layout_insensitive")

    assert result.updated == (path,)


def test_exact_mode_detects_whitespace_changes(tmp_path: Path) -> None:
    path = tmp_path / "code.txt"
    path.write_text('print("hello")\n', encoding="utf-8")

    # Same content with different spacing
    result = write_text_if_changed(path, 'print(  "hello"  )', compare_mode="exact")

    assert result.updated == (path,)
