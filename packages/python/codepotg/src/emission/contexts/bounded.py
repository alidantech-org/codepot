from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from contracts.normalized_document_contract import build_normalized_document_contract
from contracts.template import TemplateContract


class BoundedGraphContext(Mapping[str, Any]):
    """Selector-aware context that copies only bounded public globals.

    ``resolve_variable`` may read hidden selection roots through ``__getitem__``.
    ``dict(context)`` and template render contexts see only the public mapping.
    This keeps complete collections and the full API contract out of graph
    templates while preserving compatibility selection expressions.
    """

    def __init__(
        self,
        *,
        public: Mapping[str, Any],
        selection_roots: Mapping[str, Any],
    ) -> None:
        overlap = set(public) & set(selection_roots)
        if overlap:
            raise ValueError(
                "Bounded graph public and hidden roots overlap: "
                + ", ".join(sorted(overlap))
            )
        self._public = dict(public)
        self._selection_roots = dict(selection_roots)

    def __getitem__(self, key: str) -> Any:
        if key in self._public:
            return self._public[key]
        return self._selection_roots[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._public)

    def __len__(self) -> int:
        return len(self._public)

    @property
    def public_keys(self) -> tuple[str, ...]:
        return tuple(self._public)

    @property
    def selection_keys(self) -> tuple[str, ...]:
        return tuple(self._selection_roots)


def bounded_graph_context(contract: TemplateContract) -> BoundedGraphContext:
    """Build bounded globals and internal-only selection roots."""

    api_meta = getattr(contract.api, "meta", {})
    meta: Mapping[str, Any] = api_meta if isinstance(api_meta, Mapping) else {}
    document_contract = meta.get("normalized_document")
    if document_contract is None:
        document_contract = build_normalized_document_contract(contract.api.raw)

    public = {
        "project": contract.project,
        "lang": contract.lang,
        "emit": contract.emit,
        "meta": contract.meta,
        "document_contract": document_contract,
        "selected_frontend": contract.selected_frontend,
        "selected_frontends": contract.selected_frontends,
        "frontend_count": contract.frontend_count,
    }
    normalized_roots = {
        "normalized": meta.get("normalized"),
        "domains": meta.get("normalized_domains"),
        "schema_contract": meta.get("normalized_schemas"),
        "codegen_contract": meta.get("normalized_codegen"),
        "entity_contract": meta.get("normalized_entities"),
        "frontend_contract": meta.get("normalized_frontends"),
    }
    public.update(
        {
            name: value
            for name, value in normalized_roots.items()
            if value is not None
        }
    )

    selection_roots = {
        "api": contract.api,
        "resources": contract.resources,
        "features": contract.features,
        "schemas": contract.schemas,
        "operations": contract.operations,
        "entities": contract.entities,
        "frontends": contract.frontends,
    }
    return BoundedGraphContext(public=public, selection_roots=selection_roots)
