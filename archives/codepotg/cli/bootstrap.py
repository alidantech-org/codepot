"""CLI import bootstrap.

This keeps `python -m cli.main` working during local development when the
engine packages live under src/ and the CLI package lives at repository root.
Installed console scripts do not depend on this being special.
"""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_src_on_path() -> None:
    """Add the src directory to sys.path when running the CLI from source."""
    project_root = Path(__file__).resolve().parents[1]
    src_path = project_root / "src"

    if not src_path.exists():
        return

    src_text = str(src_path)
    if src_text not in sys.path:
        sys.path.insert(0, src_text)
