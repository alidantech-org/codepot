"""End-to-end emission tests with real and focused OpenAPI fixtures."""

from __future__ import annotations

from src.app.app import GeneratorApp
from tests.fixtures.templates import write_debug_templates


def test_debug_emit_end_to_end(tmp_path, real_openapi_json_path) -> None:
    """Generate the complete debug pack once from the canonical real spec."""
    template_root = write_debug_templates(tmp_path / "templates")
    output_path = tmp_path / "output"

    result = GeneratorApp().emit(
        input_path=real_openapi_json_path,
        language="debug",
        output_path=output_path,
        templates_path=template_root,
        dry_run=False,
    )

    assert result.language == "debug"
    assert result.dry_run is False
    assert result.planned
    assert result.written

    for written_path in result.written:
        assert written_path.exists()
        assert written_path.is_relative_to(output_path)

    summary_path = output_path / "summary.txt"
    assert summary_path.read_text(encoding="utf-8") == (
        "API: Alidantech API\nLanguage: debug\n"
    )

    apps_docs = output_path / "docs" / "resources" / "platform" / "apps"
    assert (apps_docs / "index.md").is_file()
    assert (apps_docs / "operations.md").is_file()
    assert (apps_docs / "schemas.md").is_file()
    assert (apps_docs / "operations" / "get_find_apps.md").is_file()
    assert (apps_docs / "schemas" / "dtos" / "app_list_query.md").is_file()
    assert (apps_docs / "schemas" / "dtos" / "create_app_body.md").is_file()
    assert (apps_docs / "schemas" / "enums" / "app_status.md").is_file()

    planned = {path.relative_to(output_path).as_posix() for path in result.planned}
    assert "docs/resources/platform/apps/index.md" in planned
    assert "docs/resources/platform/apps/operations.md" in planned
    assert "docs/resources/platform/apps/schemas.md" in planned
    assert "docs/resources/platform/apps/operations/get_find_apps.md" in planned
    assert (
        "docs/resources/platform/apps/schemas/dtos/app_list_query.md"
        in planned
    )
    assert (
        "docs/resources/platform/apps/schemas/dtos/create_app_body.md"
        in planned
    )
    assert (
        "docs/resources/platform/apps/schemas/enums/app_status.md"
        in planned
    )


def test_debug_emit_dry_run(tmp_path, project_root) -> None:
    """Verify dry-run behavior with the focused shared project fixture."""
    template_root = write_debug_templates(tmp_path / "templates")
    output_path = tmp_path / "output"
    source = project_root / "tests" / "fixtures" / "project_openapi.yaml"

    result = GeneratorApp().emit(
        input_path=source,
        language="debug",
        output_path=output_path,
        templates_path=template_root,
        dry_run=True,
    )

    assert result.dry_run is True
    assert result.planned
    assert result.written == []
    assert result.skipped
    assert not output_path.exists()
