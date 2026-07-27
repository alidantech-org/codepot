from __future__ import annotations

from codepotg.api import CancellationToken

from ..parsing.document import ParsedDocument
from .identity import ReferenceIdentity
from .pointer import join_pointer
from .resolver import ReferenceResolver


def validate_reference_graph(
    root: ParsedDocument,
    resolver: ReferenceResolver,
    cancellation: CancellationToken,
) -> None:
    visited: set[tuple[str, str]] = set()

    def walk(
        document: ParsedDocument,
        value: object,
        pointer: str,
        active: tuple[ReferenceIdentity, ...],
    ) -> None:
        cancellation.raise_if_cancelled()
        visit_key = (document.source.canonical_id, pointer)
        if visit_key in visited:
            return
        visited.add(visit_key)
        if isinstance(value, dict):
            reference = value.get("$ref")
            if isinstance(reference, str):
                source = ReferenceIdentity(document.source.canonical_id, pointer)
                resolved = resolver.resolve(
                    document=document,
                    reference=reference,
                    source_identity=source,
                    active=active,
                )
                if resolved is not None and resolved.identity not in active:
                    walk(
                        resolved.document,
                        resolved.value,
                        resolved.identity.pointer,
                        (*active, resolved.identity),
                    )
            for key, item in value.items():
                if key == "$ref" or key.startswith("x-"):
                    continue
                walk(document, item, join_pointer(pointer, key), active)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(document, item, join_pointer(pointer, index), active)

    walk(root, root.value, "", ())
