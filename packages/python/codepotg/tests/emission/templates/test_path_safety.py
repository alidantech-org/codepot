"""Tests for safe template output paths."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.emission.templates.path_safety import validate_relative_path, UnsafePathError


def test_safe_relative_path_allows_normal_path() -> None:
    validate_relative_path(Path("schemas/user/schema.txt"))


def test_safe_relative_path_rejects_parent_escape() -> None:
    with pytest.raises(UnsafePathError):
        validate_relative_path(Path("../outside.txt"))
