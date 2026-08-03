"""Template path resolution for CodepotG workflows."""

from __future__ import annotations

from pathlib import Path

from archives.codepotg.src.contracts.language import LanguageAdapter

BUNDLED_TEMPLATES_ROOT = Path(__file__).resolve().parents[2] / "codepotg" / "templates"


def resolve_template_root(
    *,
    adapter: LanguageAdapter,
    templates_path: Path | None,
) -> Path:
    """Resolve a custom pack or the bundled pack selected by the language.

    Project-owned packs must be explicit in ``Codepotg.yaml``. Omitting
    ``templateDir`` always selects the bundled pack, independent of the current
    working directory.
    """
    if templates_path is not None:
        return templates_path.expanduser().resolve()

    return (BUNDLED_TEMPLATES_ROOT / adapter.template_name).resolve()
