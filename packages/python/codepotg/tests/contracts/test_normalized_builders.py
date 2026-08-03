from __future__ import annotations

from dataclasses import dataclass

import pytest

from contracts.normalized import (
    DiagnosticCategory,
    ReferenceKind,
    ResolutionState,
)
from contracts.normalized_builders import build_reference


@dataclass(frozen=True)
class _Target:
    id: str


def test_plain_registry_names_are_internal_references() -> None:
    target = _Target(id="users")

    resolved = build_reference(
        "users",
        kind=ReferenceKind.RESOURCE,
        owner="listUsers",
        source_path="operation.resource",
        targets={"users": target},
    )
    missing = build_reference(
        "missingResource",
        kind=ReferenceKind.RESOURCE,
        owner="listUsers",
        source_path="operation.resource",
        targets={"users": target},
    )

    assert resolved.state == ResolutionState.RESOLVED
    assert resolved.target is target
    assert missing.state == ResolutionState.MISSING
    assert missing.diagnostics[0].category == DiagnosticCategory.UNRESOLVED


def test_missing_json_pointer_is_internal_and_inspectable() -> None:
    value = build_reference(
        "#/components/schemas/Missing",
        kind=ReferenceKind.SCHEMA,
        owner="User",
        source_path="components.schemas.User",
        targets={},
    )

    assert value.state == ResolutionState.MISSING
    assert value.diagnostics[0].ref == "#/components/schemas/Missing"


@pytest.mark.parametrize(
    "ref",
    [
        "https://example.test/openapi.json#/components/schemas/User",
        "other.yaml#/components/schemas/User",
        "../shared/openapi.json#/components/schemas/User",
        "file:///tmp/openapi.json#/components/schemas/User",
        "urn:example:user",
    ],
)
def test_uri_and_file_references_remain_external(ref: str) -> None:
    value = build_reference(
        ref,
        kind=ReferenceKind.SCHEMA,
        owner="User",
        source_path="components.schemas.User",
        targets={},
    )

    assert value.state == ResolutionState.EXTERNAL
    assert value.diagnostics == ()
