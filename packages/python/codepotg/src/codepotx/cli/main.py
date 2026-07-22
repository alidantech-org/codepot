# ruff: noqa: E402, I001
"""Namespaced CodepotX CLI entry point.

This prevents the global `codepotx` command from importing another project's
top-level `cli.main` module.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def _repo_root() -> Path:
    # src/codepotx/cli/main.py -> src -> repository root
    return Path(__file__).resolve().parents[3]


def _ensure_repo_cli_first() -> None:
    root = _repo_root()
    src = root / "src"

    for item in (str(root), str(src)):
        if item in sys.path:
            sys.path.remove(item)
        sys.path.insert(0, item)

    loaded_cli = sys.modules.get("cli")
    loaded_cli_file = str(getattr(loaded_cli, "__file__", "")) if loaded_cli else ""

    if loaded_cli_file and str(root) not in loaded_cli_file:
        sys.modules.pop("cli", None)
        sys.modules.pop("cli.main", None)


_ensure_repo_cli_first()

legacy_main = importlib.import_module("cli.main")

app = legacy_main.app


if __name__ == "__main__":
    app()
