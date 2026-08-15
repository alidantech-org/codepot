from __future__ import annotations

import pytest

from dryv.features.packs import (
    PackConfigurationError,
    PackTemplateResource,
    decode_pack_manifest,
    normalize_pack,
)

MANIFEST_RESOURCE = "resource://pack/example/DryvPack.yaml"


def _manifest() -> dict[str, object]:
    return {
        "apiVersion": "dryv.dev/v1",
        "id": "example/pack",
        "version": "1.0.0",
        "options": {"style": {"choices": ["class", "functions"], "default": "class"}},
        "bindings": {"base": {"required": True}},
        "selections": {"items": {"paths": ["src"], "select": "groups.schemas.each", "bindings": ["base"]}},
    }


def test_pack_manifest_normalizes_deterministically() -> None:
    manifest = decode_pack_manifest(_manifest())
    assert manifest.id == "example/pack"
    assert manifest.resolve_options(()) == (("style", "class"),)
    assert manifest.selections[0].provenance_pointer == "$.selections.items"


def test_unknown_manifest_fields_are_rejected() -> None:
    value = _manifest()
    value["templateEngines"] = {"jinja": {}}
    with pytest.raises(PackConfigurationError) as caught:
        decode_pack_manifest(value)
    assert caught.value.code == "PACK_UNKNOWN_FIELD"


def test_template_resources_have_explicit_renderer_capability_and_provenance() -> None:
    manifest = decode_pack_manifest(_manifest())
    template = PackTemplateResource(
        "resource://pack/example/templates/item.jinja",
        "templates/{items}/item.ts.jinja",
        "text/x-jinja-template",
        "jinja/v1",
        "items",
    )
    normalized = normalize_pack(manifest, (template,), manifest_resource_id=MANIFEST_RESOURCE)
    assert normalized.templates[0].renderer_capability == "jinja/v1"
    assert normalized.manifest_resource_id == MANIFEST_RESOURCE


def test_unknown_template_selection_is_rejected() -> None:
    manifest = decode_pack_manifest(_manifest())
    with pytest.raises(PackConfigurationError) as caught:
        normalize_pack(
            manifest,
            (PackTemplateResource("resource://pack/example/x", "templates/x.jinja", "text/x-jinja-template", "jinja/v1", "missing"),),
            manifest_resource_id=MANIFEST_RESOURCE,
        )
    assert caught.value.code == "PACK_MISSING_SELECTION"
