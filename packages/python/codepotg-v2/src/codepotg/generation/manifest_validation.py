from __future__ import annotations

import re
from pathlib import Path

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version as PackagingVersion

from codepotg.config import PackManifest
from codepotg.versions import CORE_VERSION, IR_API_VERSION

_COMPARATOR = re.compile(r"(?<!^)(?<![,\s])\s+(?=[<>=!~])")


def require_pack_contained(pack_root: Path, project_root: Path) -> Path:
    canonical_project = project_root.resolve(strict=True)
    canonical_pack = pack_root.resolve(strict=True)
    try:
        canonical_pack.relative_to(canonical_project)
    except ValueError as exc:
        raise ValueError("PACK_SOURCE_ESCAPE: local pack source escapes the project root") from exc
    return canonical_pack


def validate_pack_compatibility(manifest: PackManifest) -> None:
    requirements = dict(manifest.requires)
    allowed = {"codepotg", "ir"}
    unknown = sorted(set(requirements) - allowed)
    if unknown:
        raise ValueError(
            f"PACK_REQUIREMENT_UNKNOWN: unknown compatibility requirement {unknown[0]!r}"
        )
    for name, actual in (
        ("codepotg", str(CORE_VERSION)),
        ("ir", str(IR_API_VERSION.version)),
    ):
        requirement = requirements.get(name)
        if requirement is None:
            continue
        if not isinstance(requirement, str) or not requirement.strip():
            raise ValueError(f"PACK_REQUIREMENT_INVALID: {name} compatibility must be a string")
        try:
            specifier = SpecifierSet(_normalize_specifier(requirement))
        except InvalidSpecifier as exc:
            raise ValueError(
                f"PACK_REQUIREMENT_INVALID: invalid {name} compatibility specifier"
            ) from exc
        if PackagingVersion(actual) not in specifier:
            raise ValueError(
                f"PACK_REQUIREMENT_UNSATISFIED: {name} {actual} does not satisfy {requirement!r}"
            )


def validate_selection_graph(manifest: PackManifest) -> None:
    graph: dict[str, tuple[str, ...]] = {}
    for selection in manifest.selections:
        targets = tuple(
            sorted(
                {
                    *(target for _, target in selection.imports),
                    *selection.exports,
                }
            )
        )
        graph[selection.key] = targets

    visiting: set[str] = set()
    visited: set[str] = set()
    trail: list[str] = []

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            start = trail.index(node)
            cycle = " -> ".join((*trail[start:], node))
            raise ValueError(f"PLAN_SELECTION_CYCLE: generated dependency cycle detected: {cycle}")
        visiting.add(node)
        trail.append(node)
        for target in graph.get(node, ()):
            visit(target)
        trail.pop()
        visiting.remove(node)
        visited.add(node)

    for key in sorted(graph):
        visit(key)


def _normalize_specifier(value: str) -> str:
    stripped = value.strip()
    if "," in stripped:
        return stripped.replace(" ", "")
    parts = stripped.split()
    return ",".join(parts) if len(parts) > 1 else stripped
