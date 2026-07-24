from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from contracts.normalized import (
    ContractDiagnostic,
    ContractReference,
    DiagnosticCategory,
    DiagnosticLevel,
    ReferenceKind,
    ResolutionState,
    SchemaUse,
    SchemaUseKind,
)
from contracts.source import FrozenMap, freeze_source_map

T = TypeVar("T")


def build_reference(
    ref: str,
    *,
    kind: ReferenceKind,
    owner: str,
    source_path: str,
    targets: Mapping[str, T],
) -> ContractReference[T]:
    """Build a non-recursively-expanding resolved or preserved reference."""

    target = targets.get(ref)
    if target is not None:
        return ContractReference(
            ref=ref,
            kind=kind,
            name=_target_name(target),
            owner=owner,
            state=ResolutionState.RESOLVED,
            target=target,
            source_path=source_path,
        )
    if not ref.startswith("#/"):
        return ContractReference(
            ref=ref,
            kind=kind,
            owner=owner,
            state=ResolutionState.EXTERNAL,
            source_path=source_path,
        )
    diagnostic = ContractDiagnostic(
        category=DiagnosticCategory.UNRESOLVED,
        level=DiagnosticLevel.WARNING,
        message=f"Internal {kind.value} ref is unresolved: {ref}",
        source_path=source_path,
        ref=ref,
        owner=owner,
    )
    return ContractReference(
        ref=ref,
        kind=kind,
        owner=owner,
        state=ResolutionState.MISSING,
        source_path=source_path,
        diagnostics=(diagnostic,),
    )


def build_schema_use(
    value: Any,
    *,
    owner: str,
    source_path: str,
    schema_targets: Mapping[str, T],
) -> SchemaUse[T]:
    """Build a shared schema-use value from a ref or inline schema mapping."""

    raw = _mapping(value)
    if not raw:
        return SchemaUse(source_path=source_path)
    refs = tuple(
        build_reference(
            ref,
            kind=ReferenceKind.SCHEMA,
            owner=owner,
            source_path=source_path,
            targets=schema_targets,
        )
        for ref in direct_refs(raw)
    )
    primary = refs[0] if refs else None
    inline_values = {key: item for key, item in raw.items() if key != "$ref"}
    inline = freeze_source_map(inline_values) if inline_values else FrozenMap()
    resolved_targets = tuple(
        reference.target for reference in refs if reference.target is not None
    )
    schema = resolved_targets[0] if len(resolved_targets) == 1 else None
    if refs and inline:
        kind = SchemaUseKind.MIXED
    elif len(refs) > 1:
        kind = SchemaUseKind.MULTIPLE_REFERENCES
    elif refs:
        kind = SchemaUseKind.REFERENCE
    elif inline:
        kind = SchemaUseKind.INLINE
    else:
        kind = SchemaUseKind.EMPTY
    return SchemaUse(
        kind=kind,
        ref=primary,
        refs=refs,
        schema=schema,
        inline=inline,
        source_path=source_path,
        diagnostics=tuple(
            diagnostic
            for reference in refs
            for diagnostic in reference.diagnostics
        ),
    )


def direct_refs(value: Mapping[str, Any]) -> tuple[str, ...]:
    """Return direct and composition-branch refs without recursive expansion."""

    refs: list[str] = []
    direct = value.get("$ref")
    if isinstance(direct, str):
        refs.append(direct)
    for keyword in ("allOf", "anyOf", "oneOf"):
        for branch in _sequence(value.get(keyword)):
            if isinstance(branch, Mapping):
                ref = branch.get("$ref")
                if isinstance(ref, str):
                    refs.append(ref)
    return tuple(dict.fromkeys(refs))


def _target_name(target: Any) -> str | None:
    identifier = getattr(target, "id", None)
    if isinstance(identifier, str) and identifier:
        return identifier
    name = getattr(target, "name", None)
    if isinstance(name, str):
        return name or None
    for attribute in ("raw", "clean", "original"):
        value = getattr(name, attribute, None)
        if isinstance(value, str) and value:
            return value
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list | tuple) else ()
