"""Tests for portable language adapters and their complete variable baseline."""

from __future__ import annotations

import pytest
from archives.codepotg.src.languages.discovery import discover_languages, resolve_language_adapter
from archives.codepotg.tests.fixtures.contracts import make_api_contract

LANGUAGES = {
    "python": "py",
    "java": "jvm-java",
    "csharp": "dotnet",
    "go": "golang",
    "rust": "rs",
}


@pytest.mark.parametrize(("language", "alias"), LANGUAGES.items())
def test_portable_adapter_discovery_and_aliases(language: str, alias: str) -> None:
    assert language in discover_languages()
    assert resolve_language_adapter(language).name == language
    assert resolve_language_adapter(alias).name == language


@pytest.mark.parametrize("language", LANGUAGES)
def test_portable_adapters_preserve_complete_typed_contract(
    tmp_path,
    language: str,
) -> None:
    api = make_api_contract()
    adapter = resolve_language_adapter(language)

    contract = adapter.build_template_contract(
        api=api,
        output_path=tmp_path / language,
        template_root=tmp_path / "templates",
        dry_run=True,
    )

    assert contract.api is api
    assert contract.lang.name == language
    assert contract.project.lang.name == language
    assert contract.project.emit.format == language
    assert contract.emit.dry_run is True
    assert contract.meta.debug is False
    assert contract.lang.meta["complete_variable_contract"] is True
    assert contract.lang.meta["openapi_version"] == "3.1.0"
    assert contract.lang.meta["api_version"] == "v1"
    assert contract.lang.meta["server_urls"] == ("https://api.example.test",)

    assert len(contract.resources) == 1
    assert len(contract.schemas.all) == 1
    assert len(contract.schemas.emit_models) == 1
    assert len(contract.operations) == 1
    assert contract.resources[0].operations == contract.operations
    assert contract.resources[0].models == contract.schemas.emit_models
    assert contract.schemas.emit_models[0].api is api.schemas.emit_models[0]
    assert contract.operations[0].api is api.operations[0]
    assert contract.resources[0].api is api.resources[0]


@pytest.mark.parametrize("language", LANGUAGES)
def test_portable_adapter_post_actions_are_informational(tmp_path, language: str) -> None:
    adapter = resolve_language_adapter(language)
    contract = adapter.build_template_contract(
        api=make_api_contract(),
        output_path=tmp_path,
        dry_run=True,
    )

    result = adapter.after_emit(result=None)  # type: ignore[arg-type]

    assert result.diagnostics
    assert contract.lang.name == language
