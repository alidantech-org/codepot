from __future__ import annotations

import json
from pathlib import Path

from codepotg.api import CancellationToken
from codepotg.ports import SourceAdapterRequest

from codepotg_openapi import OpenApiSourceAdapter


def test_network_reference_is_denied_without_host_authority() -> None:
    document = {
        "openapi": "3.1.0",
        "info": {"title": "Network", "version": "1"},
        "paths": {},
        "components": {
            "schemas": {
                "Remote": {"$ref": "https://example.test/schema.json#/Remote"}
            }
        },
    }
    result = OpenApiSourceAdapter().normalize(
        SourceAdapterRequest(source_id="network", content=json.dumps(document)),
        CancellationToken(),
    )
    assert result.contract is None
    assert "OA_REF_NETWORK_DENIED" in {item.code for item in result.diagnostics}


def test_local_reference_cannot_escape_root_directory(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"Outside": {"type": "string"}}), encoding="utf-8")
    root = allowed / "openapi.json"
    root.write_text(
        json.dumps(
            {
                "openapi": "3.1.0",
                "info": {"title": "Contained", "version": "1"},
                "paths": {},
                "components": {
                    "schemas": {
                        "Outside": {"$ref": "../outside.json#/Outside"}
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    result = OpenApiSourceAdapter().normalize(
        SourceAdapterRequest(source_id="contained", location=str(root.resolve())),
        CancellationToken(),
    )
    assert result.contract is None
    assert "OA_SOURCE_PATH_ESCAPE" in {item.code for item in result.diagnostics}
