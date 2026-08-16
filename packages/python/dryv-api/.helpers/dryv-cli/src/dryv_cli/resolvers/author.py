from __future__ import annotations

from dataclasses import dataclass

from dryv_cli.project import LocalProject


@dataclass(frozen=True, slots=True)
class ResolvedAuthor:
    target: str


def resolve_author(project: LocalProject, override: str | None = None) -> ResolvedAuthor | None:
    target = override or project.locators.source_author
    return None if target is None else ResolvedAuthor(target)


__all__ = ["ResolvedAuthor", "resolve_author"]
