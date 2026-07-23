# ruff: noqa: E402, I001
"""Namespaced CodepotG CLI entry point.

The implementation is still packaged in the legacy top-level ``cli`` module.
This wrapper puts the bundled module location first for both editable source
checkouts and installed wheels, avoiding collisions with unrelated packages
named ``cli``.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def _legacy_module_root() -> Path:
    current = Path(__file__).resolve()

    # Installed wheel: site-packages/codepotg/cli/main.py with site-packages/cli.
    installed_root = current.parents[2]
    if (installed_root / "cli" / "main.py").is_file():
        return installed_root

    # Source checkout: <project>/src/codepotg/cli/main.py with <project>/cli.
    source_root = current.parents[3]
    if (source_root / "cli" / "main.py").is_file():
        return source_root

    raise RuntimeError("The bundled CodepotG CLI implementation could not be located.")


def _ensure_bundled_cli_first() -> None:
    root = _legacy_module_root()
    candidates = [root]
    source = root / "src"
    if source.is_dir():
        candidates.append(source)

    for item in reversed(candidates):
        value = str(item)
        if value in sys.path:
            sys.path.remove(value)
        sys.path.insert(0, value)

    loaded_cli = sys.modules.get("cli")
    loaded_cli_file = Path(str(getattr(loaded_cli, "__file__", ""))).resolve() if loaded_cli else None
    if loaded_cli_file and root not in loaded_cli_file.parents:
        sys.modules.pop("cli", None)
        sys.modules.pop("cli.main", None)


_ensure_bundled_cli_first()
legacy_main = importlib.import_module("cli.main")
app = legacy_main.app


if __name__ == "__main__":
    app()
