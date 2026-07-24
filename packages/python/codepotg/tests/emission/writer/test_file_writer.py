"""Tests for changed-aware atomic file writing."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.emission.writer import file_writer
from src.emission.writer.file_writer import write_bytes_if_changed, write_text_if_changed


def test_write_text_if_changed_creates_file(tmp_path: Path) -> None:
    path = tmp_path / "hello.txt"

    result = write_text_if_changed(path, "hello")

    assert path.read_text(encoding="utf-8") == "hello\n"
    assert result.created == (path,)
    assert not tuple(tmp_path.glob(".*.tmp"))


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
    assert not tuple(tmp_path.glob(".*.tmp"))


def test_write_bytes_if_changed_is_atomic_and_changed_aware(tmp_path: Path) -> None:
    path = tmp_path / "asset.bin"

    created = write_bytes_if_changed(path, b"first")
    unchanged = write_bytes_if_changed(path, b"first")
    updated = write_bytes_if_changed(path, b"second")

    assert created.created == (path,)
    assert unchanged.unchanged == (path,)
    assert updated.updated == (path,)
    assert path.read_bytes() == b"second"
    assert not tuple(tmp_path.glob(".*.tmp"))


def test_atomic_replace_failure_preserves_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "hello.txt"
    path.write_text("old\n", encoding="utf-8")

    def fail_replace(source: Path, target: Path) -> None:
        raise OSError(f"cannot replace {source} with {target}")

    monkeypatch.setattr(file_writer.os, "replace", fail_replace)

    with pytest.raises(OSError, match="cannot replace"):
        write_text_if_changed(path, "new")

    assert path.read_text(encoding="utf-8") == "old\n"
    assert not tuple(tmp_path.glob(".*.tmp"))


def test_layout_insensitive_ignores_whitespace_outside_strings(tmp_path: Path) -> None:
    path = tmp_path / "code.txt"
    path.write_text('print("hello world")\n', encoding="utf-8")

    result = write_text_if_changed(
        path,
        'print(  "hello world"  )',
        compare_mode="layout_insensitive",
    )

    assert result.unchanged == (path,)


def test_layout_insensitive_detects_string_content_changes(tmp_path: Path) -> None:
    path = tmp_path / "code.txt"
    path.write_text('print("hello world")\n', encoding="utf-8")

    result = write_text_if_changed(
        path,
        'print("helloworld")',
        compare_mode="layout_insensitive",
    )

    assert result.updated == (path,)


def test_layout_insensitive_detects_code_changes(tmp_path: Path) -> None:
    path = tmp_path / "code.txt"
    path.write_text('print("hello")\n', encoding="utf-8")

    result = write_text_if_changed(
        path,
        'console.log("hello")',
        compare_mode="layout_insensitive",
    )

    assert result.updated == (path,)


def test_exact_mode_detects_whitespace_changes(tmp_path: Path) -> None:
    path = tmp_path / "code.txt"
    path.write_text('print("hello")\n', encoding="utf-8")

    result = write_text_if_changed(path, 'print(  "hello"  )', compare_mode="exact")

    assert result.updated == (path,)
