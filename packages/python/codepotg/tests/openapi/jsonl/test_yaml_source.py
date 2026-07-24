from __future__ import annotations

import json
from pathlib import Path

import pytest

from openapi.jsonl import JsonlInputError, compile_openapi_source_jsonl


def test_yaml_source_compiles_with_warning_metadata_and_reuse(tmp_path: Path) -> None:
    source = tmp_path / "openapi.yaml"
    source.write_text(
        """
openapi: 3.1.0
info:
  title: YAML API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: listUsers
      responses:
        "200":
          description: OK
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
""".strip(),
        encoding="utf-8",
    )
    events = []
    cache = tmp_path / "cache"

    first = compile_openapi_source_jsonl(source, cache, progress=events.append)
    second = compile_openapi_source_jsonl(source, cache, progress=events.append)

    assert not first.reused
    assert second.reused
    assert first.manifest.sections["paths"].count == 1
    assert first.manifest.sections["components/schemas"].count == 1
    assert first.manifest.source["path"] == "openapi.yaml"
    assert first.manifest.source["format"] == "yaml"
    assert first.manifest.source["compiledFormat"] == "json"
    assert str(first.manifest.source["originalSha256"]).startswith("sha256:")
    assert "JSON" in str(first.manifest.source["compatibilityWarning"])
    assert any(
        event.get("stage") == "input"
        and event.get("status") == "compatibility"
        and event.get("format") == "yaml"
        for event in events
    )

    manifest = json.loads((cache / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source"]["path"] == "openapi.yaml"
    assert manifest["source"]["format"] == "yaml"


def test_yaml_and_equivalent_json_have_matching_section_counts(tmp_path: Path) -> None:
    document = {
        "openapi": "3.1.0",
        "info": {"title": "Equivalent", "version": "1.0.0"},
        "paths": {"/health": {"get": {"responses": {"200": {"description": "OK"}}}}},
        "components": {"schemas": {"Health": {"type": "string"}}},
    }
    json_source = tmp_path / "openapi.json"
    yaml_source = tmp_path / "openapi.yml"
    json_source.write_text(json.dumps(document), encoding="utf-8")
    yaml_source.write_text(
        """
openapi: 3.1.0
info:
  title: Equivalent
  version: 1.0.0
paths:
  /health:
    get:
      responses:
        "200":
          description: OK
components:
  schemas:
    Health:
      type: string
""".strip(),
        encoding="utf-8",
    )

    json_result = compile_openapi_source_jsonl(json_source, tmp_path / "json-cache")
    yaml_result = compile_openapi_source_jsonl(yaml_source, tmp_path / "yaml-cache")

    assert {
        name: section.count for name, section in json_result.manifest.sections.items()
    } == {
        name: section.count for name, section in yaml_result.manifest.sections.items()
    }


def test_yaml_source_rejects_non_object_root(tmp_path: Path) -> None:
    source = tmp_path / "openapi.yaml"
    source.write_text("- one\n- two\n", encoding="utf-8")

    with pytest.raises(JsonlInputError, match="root must be an object"):
        compile_openapi_source_jsonl(source, tmp_path / "cache")


def test_source_compiler_rejects_unknown_extension(tmp_path: Path) -> None:
    source = tmp_path / "openapi.txt"
    source.write_text("{}", encoding="utf-8")

    with pytest.raises(JsonlInputError, match="Unsupported OpenAPI source extension"):
        compile_openapi_source_jsonl(source, tmp_path / "cache")
