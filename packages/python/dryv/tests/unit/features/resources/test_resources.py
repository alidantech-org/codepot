from __future__ import annotations

from io import BytesIO

import pytest

from dryv.features.resources import (
    ResourceError,
    ResourceId,
    ResourceIdError,
    ResourceManifest,
    ResourceManifestEntry,
    ResourceRegistry,
    resource_id,
)


def test_in_memory_resource_is_content_addressed_and_reusable() -> None:
    registry = ResourceRegistry()
    first = registry.register_bytes("resource://project/dryv.yaml", "application/yaml", b"name: example\n")
    second = registry.register_bytes("resource://project/dryv.yaml", "application/yaml", b"name: example\n")
    assert second is first
    assert first.descriptor.content_hash is not None
    assert registry.get_by_hash(first.descriptor.content_hash) is first
    assert registry.read(first.descriptor.id) == b"name: example\n"


def test_conflicting_logical_id_fails_clearly() -> None:
    registry = ResourceRegistry()
    registry.register_bytes("resource://ir/main.json", "application/json", b"{}")
    with pytest.raises(ResourceError) as caught:
        registry.register_bytes("resource://ir/main.json", "application/json", b'{"changed":true}')
    assert caught.value.code == "RESOURCE_ID_CONFLICT"


def test_streamed_resource_is_bounded_and_can_be_read_in_chunks() -> None:
    registry = ResourceRegistry(max_resource_bytes=12)
    resource = registry.register_stream("resource://pack/api/template.hbs", "text/x-handlebars-template", BytesIO(b"hello world"), chunk_bytes=3)
    assert b"".join(registry.iter_bytes(resource.descriptor.id, chunk_bytes=2)) == b"hello world"
    with pytest.raises(ResourceError) as caught:
        registry.register_stream("resource://pack/api/too-large.hbs", "text/plain", BytesIO(b"0123456789abc"))
    assert caught.value.code == "RESOURCE_LIMIT"


def test_supplied_hash_is_verified() -> None:
    registry = ResourceRegistry()
    with pytest.raises(ResourceError) as caught:
        registry.register_bytes("resource://ir/main.json", "application/json", b"{}", content_hash="sha256:" + "0" * 64)
    assert caught.value.code == "RESOURCE_HASH_MISMATCH"


def test_manifest_reports_only_missing_content_addressed_blobs() -> None:
    registry = ResourceRegistry()
    present = registry.register_bytes("resource://project/dryv.yaml", "application/yaml", b"name: example")
    wanted_hash = "sha256:" + "1" * 64
    manifest = ResourceManifest((
        ResourceManifestEntry(ResourceId("resource://project/dryv.yaml"), "application/yaml", len(present.content), present.descriptor.content_hash),
        ResourceManifestEntry(ResourceId("resource://ir/main.jsonl"), "application/jsonl", 10, wanted_hash),
    ))
    missing = registry.missing(manifest)
    assert tuple(str(item.id) for item in missing) == ("resource://ir/main.jsonl",)
    assert registry.missing_hashes(manifest) == (wanted_hash,)


def test_resource_ids_are_portable_and_normalize_relative_names() -> None:
    identity = resource_id("pack", "backend/templates/entity.ts.hbs")
    assert str(identity) == "resource://pack/backend/templates/entity.ts.hbs"
    assert identity.namespace == "pack"
    assert identity.path == "backend/templates/entity.ts.hbs"
    with pytest.raises(ResourceIdError):
        ResourceId("resource://project/../secrets.txt")
    with pytest.raises(ResourceIdError):
        ResourceId("C:\\project\\dryv.yaml")


def test_read_limit_is_enforced_even_for_registered_resource() -> None:
    registry = ResourceRegistry()
    registry.register_bytes("resource://project/blob.bin", "application/octet-stream", b"0123456789")
    with pytest.raises(ResourceError) as caught:
        registry.read("resource://project/blob.bin", max_bytes=4)
    assert caught.value.code == "RESOURCE_READ_LIMIT"
