from __future__ import annotations

from codepotg.diagnostics import SourceIdentity, SourceKind
from codepotg_openapi.diagnostics import DiagnosticBag
from codepotg_openapi.loading.source import LoadedSource
from codepotg_openapi.parsing.parser import DocumentParser


def _source(content: str) -> LoadedSource:
    return LoadedSource(
        identity=SourceIdentity(SourceKind.MEMORY, "parser-test"),
        canonical_id="memory:parser-test",
        logical_id="memory:parser-test",
        content=content.encode(),
    )


def test_safe_json_and_yaml_parse_to_equivalent_values() -> None:
    parser = DocumentParser()
    json_bag = DiagnosticBag()
    yaml_bag = DiagnosticBag()
    json_doc = parser.parse(
        _source('{"openapi":"3.1.0","info":{"title":"API","version":"1"},"paths":{}}'),
        json_bag,
    )
    yaml_doc = parser.parse(
        _source("openapi: 3.1.0\ninfo: {title: API, version: '1'}\npaths: {}\n"),
        yaml_bag,
    )
    assert json_doc is not None
    assert yaml_doc is not None
    assert json_doc.value == yaml_doc.value
    assert not json_bag.has_errors
    assert not yaml_bag.has_errors


def test_duplicate_yaml_key_is_diagnostic() -> None:
    diagnostics = DiagnosticBag()
    document = DocumentParser().parse(
        _source("openapi: 3.1.0\ninfo: {title: API, title: Again, version: '1'}\npaths: {}\n"),
        diagnostics,
    )
    assert document is None
    assert {item.code for item in diagnostics.freeze()} == {"OA_PARSE_DUPLICATE_KEY"}
