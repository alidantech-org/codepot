from __future__ import annotations

from constants.openapi import OPERATION_PREFIX
from inference.models import InferredDependency, InferredOperation, InferredSchema
from inference.operations.dependencies import collect_operation_dependencies


def collect_dependencies(
    schemas: tuple[InferredSchema, ...],
    operations: tuple[InferredOperation, ...],
) -> tuple[InferredDependency, ...]:
    dependencies: list[InferredDependency] = []

    for schema in schemas:
        for target_ref in schema.dependencies:
            dependencies.append(
                InferredDependency(
                    source_ref=schema.ref,
                    target_ref=target_ref,
                )
            )

    for operation in operations:
        source_ref = f"{OPERATION_PREFIX}{operation.operation_id}"

        for target_ref in collect_operation_dependencies(operation):
            dependencies.append(
                InferredDependency(
                    source_ref=source_ref,
                    target_ref=target_ref,
                )
            )

    return tuple(_dedupe_dependencies(dependencies))


def _dedupe_dependencies(
    dependencies: list[InferredDependency],
) -> list[InferredDependency]:
    seen: set[tuple[str, str]] = set()
    result: list[InferredDependency] = []

    for dependency in dependencies:
        key = (dependency.source_ref, dependency.target_ref)
        if key in seen:
            continue

        seen.add(key)
        result.append(dependency)

    return result
