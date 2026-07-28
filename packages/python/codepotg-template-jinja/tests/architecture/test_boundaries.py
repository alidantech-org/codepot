from __future__ import annotations

import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PACKAGE_ROOT / "src" / "codepotg_template_jinja"


def python_sources() -> tuple[Path, ...]:
    return tuple(sorted(SOURCE_ROOT.rglob("*.py")))


def test_only_published_codepotg_namespaces_are_imported() -> None:
    allowed = {
        "codepotg",
        "codepotg.api",
        "codepotg.diagnostics",
        "codepotg.ir",
        "codepotg.plugins",
        "codepotg.ports",
        "codepotg.versions",
    }
    imported: set[str] = set()
    for path in python_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(
                    alias.name
                    for alias in node.names
                    if alias.name == "codepotg" or alias.name.startswith("codepotg.")
                )
            elif isinstance(node, ast.ImportFrom) and (
                (node.module or "") == "codepotg" or (node.module or "").startswith("codepotg.")
            ):
                imported.add(node.module or "")
    forbidden = {
        name
        for name in imported
        if not any(name == item or name.startswith(item + ".") for item in allowed)
    }
    assert not forbidden
    assert not any("codepotg.domain" in name for name in imported)
    assert not any("codepotg.application" in name for name in imported)
    assert not any("codepotg.infrastructure" in name for name in imported)
    assert not any("codepotg.runtime" in name for name in imported)
    assert not any("codepotg.cli" in name for name in imported)


def test_source_has_no_cross_adapter_or_old_renderer_imports() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in python_sources())
    forbidden = (
        "codepotg_openapi",
        "codepotg_language_typescript",
        "codepotg_language_dart",
        "codepotg_pack_",
        "src.emission.templates.renderer",
        "emission.templates.renderer",
    )
    assert all(item not in text for item in forbidden)


def test_source_has_no_filesystem_network_environment_or_process_loader() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in python_sources())
    forbidden = (
        "FileSystemLoader",
        "PackageLoader",
        "ChoiceLoader",
        "PrefixLoader",
        "FunctionLoader",
        "os.environ",
        "getenv(",
        "subprocess",
        "socket.",
        "urllib",
        "requests",
        "httpx",
        "Path(",
    )
    assert all(item not in text for item in forbidden)


def test_no_module_level_mutable_environment_cache_or_registry() -> None:
    forbidden_calls = {"Environment", "SandboxedEnvironment", "BoundedCache", "HelperRegistry"}
    for path in python_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                target_names: tuple[str, ...] = ()
                if isinstance(node, ast.Assign):
                    target_names = tuple(
                        target.id for target in node.targets if isinstance(target, ast.Name)
                    )
                elif isinstance(node.target, ast.Name):
                    target_names = (node.target.id,)
                guarded = any(
                    token in name.lower()
                    for name in target_names
                    for token in ("environment", "cache", "registry")
                )
                if guarded and isinstance(value, (ast.Dict, ast.List, ast.Set)):
                    raise AssertionError(f"module-level mutable state in {path}")
                if isinstance(value, ast.Call):
                    name = getattr(value.func, "id", None) or getattr(value.func, "attr", None)
                    assert name not in forbidden_calls, f"module-level {name} in {path}"


def test_no_target_renderer_writer_command_or_output_path_behavior() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in python_sources())
    forbidden = (
        "render_typescript",
        "render_dart",
        "output_path",
        "destination_path",
        "write_text",
        "write_bytes",
        "command_executor",
        "artifact_writer",
        "paths.yaml",
    )
    assert all(item not in text for item in forbidden)


def test_no_hard_coded_generated_target_syntax() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in python_sources())
    forbidden = (
        "export interface ",
        "import type {",
        "class-validator",
        "class extends ",
        "package:flutter",
    )
    assert all(item not in text for item in forbidden)


def test_no_same_name_module_package_collisions() -> None:
    modules = {path.stem for path in SOURCE_ROOT.glob("*.py") if path.name != "__init__.py"}
    packages = {path.name for path in SOURCE_ROOT.iterdir() if path.is_dir()}
    assert modules.isdisjoint(packages)


def test_package_scope_contains_no_github_automation() -> None:
    assert not (PACKAGE_ROOT / ".github").exists()
