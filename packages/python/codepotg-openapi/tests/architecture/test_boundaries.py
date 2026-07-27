from __future__ import annotations

import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PACKAGE_ROOT / "src" / "codepotg_openapi"


def _imports(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.append(node.module)
    return tuple(result)


def test_adapter_uses_only_public_codepotg_namespaces() -> None:
    forbidden = (
        "codepotg.domain",
        "codepotg.application",
        "codepotg.infrastructure",
        "codepotg_openapi.x_codegen",
    )
    for path in SOURCE_ROOT.rglob("*.py"):
        for imported in _imports(path):
            assert not imported.startswith(forbidden), (path, imported)


def test_source_adapter_does_not_import_targets_templates_or_writers() -> None:
    forbidden = (
        "codepotg_language_",
        "codepotg_template_",
        "jinja2",
        "codepotg.writers",
        "codepotg.planning",
    )
    for path in SOURCE_ROOT.rglob("*.py"):
        for imported in _imports(path):
            assert not imported.startswith(forbidden), (path, imported)


def test_package_has_no_target_template_or_writer_subsystems() -> None:
    forbidden_names = {"targets", "templates", "writers", "packs", "x_codegen"}
    directories = {path.name for path in SOURCE_ROOT.rglob("*") if path.is_dir()}
    assert forbidden_names.isdisjoint(directories)


def test_distribution_contains_real_adapter_and_no_github_automation() -> None:
    assert (SOURCE_ROOT / "adapter.py").is_file()
    assert not (PACKAGE_ROOT / ".github").exists()


def test_plugin_does_not_advertise_unimplemented_codegen() -> None:
    plugin = (SOURCE_ROOT / "plugin.py").read_text(encoding="utf-8")
    assert "x-codegen.versioned" not in plugin
