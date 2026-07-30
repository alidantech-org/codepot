"""Compatibility rendering coverage for normalized public template roots."""

from __future__ import annotations

from types import SimpleNamespace

from emission.templates.renderer import _with_normalized_roots


def test_eager_renderer_reuses_precomputed_normalized_roots() -> None:
    document = object()
    normalized = object()
    domains = object()
    schemas = object()
    codegen = object()
    entities = object()
    frontends = object()
    api = SimpleNamespace(
        raw={"openapi": "3.1.0"},
        meta={
            "normalized_document": document,
            "normalized": normalized,
            "normalized_domains": domains,
            "normalized_schemas": schemas,
            "normalized_codegen": codegen,
            "normalized_entities": entities,
            "normalized_frontends": frontends,
        },
    )

    context = _with_normalized_roots({"api": api, "project": object()})

    assert context["document_contract"] is document
    assert context["normalized"] is normalized
    assert context["domains"] is domains
    assert context["schema_contract"] is schemas
    assert context["codegen_contract"] is codegen
    assert context["entity_contract"] is entities
    assert context["frontend_contract"] is frontends


def test_eager_renderer_builds_safe_document_fallback() -> None:
    api = SimpleNamespace(
        raw={
            "openapi": "3.1.0",
            "info": {"title": "Fallback API", "version": "v1"},
            "paths": {},
        },
        meta={},
    )

    context = _with_normalized_roots({"api": api})
    document = context["document_contract"]

    assert document.openapi.value == "3.1.0"
    assert document.info.title.value == "Fallback API"
    assert dict(document.paths) == {}


def test_bounded_render_mapping_without_api_is_not_augmented() -> None:
    context = {"project": object(), "document_contract": object()}

    rendered = _with_normalized_roots(context)

    assert rendered is context
    assert set(rendered) == {"project", "document_contract"}
