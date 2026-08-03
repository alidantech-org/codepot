from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

import pytest

_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def test_documentation_relative_links_resolve() -> None:
    docs = Path(__file__).resolve().parents[2] / "docs"
    failures: list[str] = []

    for document in sorted(docs.rglob("*.md")):
        text = document.read_text(encoding="utf-8")
        for target in _LINK.findall(text):
            normalized = target.strip().split(maxsplit=1)[0].strip("<>")
            if not normalized or normalized.startswith(("#", "http://", "https://", "mailto:")):
                continue
            relative = unquote(normalized.split("#", 1)[0])
            resolved = (document.parent / relative).resolve()
            if not resolved.exists():
                failures.append(
                    f"{document.relative_to(docs)} -> {normalized} ({resolved})"
                )

    assert not failures, "Broken documentation links:\n" + "\n".join(failures)


@pytest.mark.parametrize(
    "required",
    (
        "paths-yaml.md",
        "template-authoring.md",
        "template-variables.md",
        "normalized-contract.md",
        "x-codegen-metadata.md",
        "openapi-preservation.md",
        "language-adapters.md",
        "compatibility.md",
    ),
)
def test_documentation_index_links_required_guides(required: str) -> None:
    docs = Path(__file__).resolve().parents[2] / "docs"
    index = (docs / "README.md").read_text(encoding="utf-8")

    assert f"({required})" in index
