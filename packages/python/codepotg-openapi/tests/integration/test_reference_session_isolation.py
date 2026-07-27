from __future__ import annotations

import json

from codepotg.api import CancellationToken
from codepotg.ports import SourceAdapterRequest

from codepotg_openapi import OpenApiSourceAdapter
from codepotg_openapi.loading import CallableReferenceLoader


def _root() -> str:
    return json.dumps(
        {
            "openapi": "3.1.0",
            "info": {"title": "References", "version": "1"},
            "paths": {},
            "components": {
                "schemas": {
                    "First": {"$ref": "https://example.test/schemas.json#/Shared"},
                    "Second": {"$ref": "https://example.test/schemas.json#/Shared"},
                }
            },
        }
    )


def test_reference_loader_is_once_per_session_and_reloaded_next_session() -> None:
    calls: list[str] = []

    def load(identity: str, cancellation: CancellationToken) -> str:
        cancellation.raise_if_cancelled()
        calls.append(identity)
        sequence = len(calls)
        return json.dumps(
            {
                "Shared": {
                    "type": "object",
                    "properties": {"session": {"const": sequence}},
                }
            }
        )

    adapter = OpenApiSourceAdapter(
        reference_loader=CallableReferenceLoader(load, authority_id="session-test")
    )
    request = SourceAdapterRequest(
        source_id="same",
        content=_root(),
        options=(("externalReferences", "controlled"),),
    )
    first = adapter.normalize(request, CancellationToken())
    second = adapter.normalize(request, CancellationToken())
    assert first.contract is not None and second.contract is not None
    assert calls == [
        "https://example.test/schemas.json",
        "https://example.test/schemas.json",
    ]
    assert first.digest != second.digest
