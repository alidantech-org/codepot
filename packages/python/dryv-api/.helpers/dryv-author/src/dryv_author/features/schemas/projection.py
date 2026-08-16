from __future__ import annotations

from dataclasses import replace

from .model import FieldDeclaration, ProjectionStep


def apply_projections(source_fields: tuple[FieldDeclaration, ...], steps: tuple[ProjectionStep, ...]) -> tuple[FieldDeclaration, ...]:
    fields = list(source_fields)
    for step in steps:
        names = {item.name for item in fields}
        missing = sorted(set(step.fields) - names)
        if missing:
            raise ValueError(f"projection references unknown fields: {', '.join(missing)}")
        if step.operation == "pick":
            wanted = set(step.fields)
            fields = [item for item in fields if item.name in wanted]
        elif step.operation == "omit":
            omitted = set(step.fields)
            fields = [item for item in fields if item.name not in omitted]
        elif step.operation == "partial":
            selected = set(step.fields)
            fields = [replace(item, options=replace(item.options, required=False if not selected or item.name in selected else item.options.required)) for item in fields]
        elif step.operation == "extend":
            collisions = names.intersection(item.name for item in step.additions)
            if collisions:
                raise ValueError(f"projection additions collide: {', '.join(sorted(collisions))}")
            fields.extend(step.additions)
    return tuple(fields)


__all__ = ["apply_projections"]
