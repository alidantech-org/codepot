from __future__ import annotations

import pytest

from app.workflows.normalization import ALL_NORMALIZED_ROOTS, required_normalized_roots


def test_bundled_debug_pack_uses_compatibility_fast_path(
    bundled_templates_root,
) -> None:
    assert required_normalized_roots(bundled_templates_root / "debug") == frozenset()


def test_compatibility_template_requires_no_normalized_roots(tmp_path) -> None:
    (tmp_path / "report.md.j2").write_text(
        "{{ api.info.title }} {{ schemas.all | length }}",
        encoding="utf-8",
    )

    assert required_normalized_roots(tmp_path) == frozenset()


def test_explicit_template_roots_include_dependencies(tmp_path) -> None:
    (tmp_path / "report.ts.j2").write_text(
        "{{ schema_contract.by_id }} {{ codegen_contract.resources }}",
        encoding="utf-8",
    )

    assert required_normalized_roots(tmp_path) == frozenset(
        {
            "normalized_schemas",
            "normalized_codegen",
            "normalized_domains",
            "normalized_entities",
        }
    )


def test_dynamic_api_meta_access_falls_back_to_all_roots(tmp_path) -> None:
    (tmp_path / "report.txt.j2").write_text(
        "{{ api.meta[selected_root] }}",
        encoding="utf-8",
    )

    assert required_normalized_roots(tmp_path) == ALL_NORMALIZED_ROOTS


def test_environment_override_can_force_or_disable_roots(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "report.txt.j2").write_text(
        "{{ codegen_contract.resources }}",
        encoding="utf-8",
    )

    monkeypatch.setenv("CODEPOTG_NORMALIZED_ROOTS", "none")
    assert required_normalized_roots(tmp_path) == frozenset()

    monkeypatch.setenv("CODEPOTG_NORMALIZED_ROOTS", "all")
    assert required_normalized_roots(tmp_path) == ALL_NORMALIZED_ROOTS

    monkeypatch.setenv("CODEPOTG_NORMALIZED_ROOTS", "missing")
    with pytest.raises(ValueError, match="Unknown CODEPOTG_NORMALIZED_ROOTS"):
        required_normalized_roots(tmp_path)
