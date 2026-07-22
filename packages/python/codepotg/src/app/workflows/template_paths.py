"""Template path resolution for app workflows."""

from __future__ import annotations

from pathlib import Path

from contracts.language import LanguageAdapter

DEFAULT_TEMPLATES_ROOT = Path("templates")
BUNDLED_TEMPLATES_ROOT = Path(__file__).resolve().parents[2] / "codepotg" / "templates"


def resolve_template_root(
    *,
    adapter: LanguageAdapter,
    templates_path: Path | None,
) -> Path:
    """Resolve the template root for a language adapter."""
    if templates_path is not None:
        return templates_path

    source_template_root = DEFAULT_TEMPLATES_ROOT / adapter.template_name
    if source_template_root.exists():
        return source_template_root

    return BUNDLED_TEMPLATES_ROOT / adapter.template_name
