from __future__ import annotations

import ast
import importlib
import tomllib
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[2]
SOURCE_ROOT = PACKAGE_ROOT / "src" / "dryv"
FEATURE_ROOT = SOURCE_ROOT / "features"
RUNTIME_ROOT = SOURCE_ROOT / "runtime"

APPROVED_FEATURES = {
    "artifacts",
    "authoring",
    "cache",
    "diagnostics",
    "hashing",
    "ir",
    "packs",
    "planning",
    "project",
    "resources",
    "scheduling",
    "serialization",
    "templating",
}

FORBIDDEN_LEGACY_PACKAGES = {"plugins", "ports"}
FORBIDDEN_PROJECT_WRITER_FILES = {
    "application/write.py",
    "infrastructure/ownership.py",
    "infrastructure/writers.py",
}
FORBIDDEN_PROJECT_WRITER_SYMBOLS = {
    "ManagedFilesystemWriter",
    "ManagedWriteReport",
    "generate_to_files",
}
FORBIDDEN_TEMPLATE_IMPORTS = {"jinja2", "handlebars", "mako", "chevron"}
FORBIDDEN_AUTHOR_IMPORTS = {"dryv_author"}
FORBIDDEN_SERVER_IMPORT_PREFIXES = (
    "aiohttp.web",
    "django",
    "fastapi",
    "flask",
    "http.server",
    "hypercorn",
    "sanic",
    "socketserver",
    "starlette",
    "tornado.web",
    "uvicorn",
    "websockets",
)


def test_feature_catalog_is_exact_and_importable() -> None:
    present = {
        path.name
        for path in FEATURE_ROOT.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    }
    assert present == APPROVED_FEATURES
    for feature in sorted(APPROVED_FEATURES):
        assert importlib.import_module(f"dryv.features.{feature}")


def test_legacy_plugin_and_port_packages_are_gone() -> None:
    present = {
        path.name
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    }
    assert present.isdisjoint(FORBIDDEN_LEGACY_PACKAGES)
    assert not (RUNTIME_ROOT / "plugins.py").exists()
    assert not (RUNTIME_ROOT / "session.py").exists()
    assert not (RUNTIME_ROOT / "composition.py").exists()


def test_engine_side_project_writer_paths_and_symbols_are_absent() -> None:
    for relative in FORBIDDEN_PROJECT_WRITER_FILES:
        assert not (SOURCE_ROOT / relative).exists(), relative

    violations: list[str] = []
    for path in SOURCE_ROOT.rglob("*.py"):
        tree = _tree(path)
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in FORBIDDEN_PROJECT_WRITER_SYMBOLS:
                    violations.append(f"{_relative(path)}:{node.name}")
    assert violations == []


def test_features_do_not_import_runtime_or_sibling_features() -> None:
    violations: list[str] = []
    for feature in sorted(APPROVED_FEATURES):
        for path in (FEATURE_ROOT / feature).rglob("*.py"):
            for imported in _imports(path):
                if imported == "dryv.runtime" or imported.startswith("dryv.runtime."):
                    violations.append(f"{_relative(path)} imports Runtime: {imported}")
                sibling = _feature_name(imported)
                if sibling is not None and sibling != feature:
                    violations.append(
                        f"{_relative(path)} imports sibling Feature {sibling}: {imported}"
                    )
    assert violations == []


def test_canonical_ir_does_not_import_runtime_or_features() -> None:
    violations: list[str] = []
    for path in (SOURCE_ROOT / "ir").rglob("*.py"):
        for imported in _imports(path):
            if imported == "dryv.runtime" or imported.startswith("dryv.runtime."):
                violations.append(f"{_relative(path)} imports Runtime: {imported}")
            if imported == "dryv.features" or imported.startswith("dryv.features."):
                violations.append(f"{_relative(path)} imports Feature: {imported}")
    assert violations == []


def test_runtime_is_only_dryv_owner_allowed_to_coordinate_multiple_features() -> None:
    violations: list[str] = []
    for path in SOURCE_ROOT.rglob("*.py"):
        if _inside(path, RUNTIME_ROOT) or _inside(path, FEATURE_ROOT):
            continue
        used = {
            feature
            for feature in (_feature_name(module) for module in _imports(path))
            if feature is not None
        }
        if len(used) > 1:
            violations.append(f"{_relative(path)} coordinates {sorted(used)!r}")
    assert violations == []


def test_runtime_contains_no_template_engine_author_backend_or_server_host() -> None:
    project = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependency_names = {
        str(item).split("[", 1)[0].split("<", 1)[0].split(">", 1)[0].split("=", 1)[0].strip().lower()
        for item in project.get("project", {}).get("dependencies", [])
    }
    assert dependency_names.isdisjoint(FORBIDDEN_TEMPLATE_IMPORTS | FORBIDDEN_AUTHOR_IMPORTS)

    violations: list[str] = []
    for path in SOURCE_ROOT.rglob("*.py"):
        for imported in _imports(path):
            root = imported.split(".", 1)[0]
            if root in FORBIDDEN_TEMPLATE_IMPORTS or root in FORBIDDEN_AUTHOR_IMPORTS:
                violations.append(f"{_relative(path)} imports {imported}")
            if imported.startswith(FORBIDDEN_SERVER_IMPORT_PREFIXES):
                violations.append(f"{_relative(path)} imports server host {imported}")
    assert violations == []


def test_runtime_public_files_are_feature_composition_only() -> None:
    assert (RUNTIME_ROOT / "engine.py").is_file()
    assert (RUNTIME_ROOT / "contracts.py").is_file()
    assert (RUNTIME_ROOT / "facade.py").is_file()
    assert (RUNTIME_ROOT / "__init__.py").is_file()


def _tree(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imports(path: Path) -> tuple[str, ...]:
    module_name = _module_name(path)
    package_name = module_name if path.name == "__init__.py" else module_name.rsplit(".", 1)[0]
    result: list[str] = []
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Import):
            result.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module:
                    result.append(node.module)
                    if node.module == "dryv.features":
                        result.extend(
                            f"dryv.features.{alias.name}"
                            for alias in node.names
                            if alias.name in APPROVED_FEATURES
                        )
                continue
            parts = package_name.split(".")
            ascend = node.level - 1
            if ascend > len(parts):
                continue
            base = parts[: len(parts) - ascend]
            if node.module:
                result.append(".".join((*base, node.module)))
            else:
                result.extend(".".join((*base, alias.name)) for alias in node.names)
    return tuple(result)


def _feature_name(module: str) -> str | None:
    parts = module.split(".")
    if len(parts) >= 3 and parts[:2] == ["dryv", "features"] and parts[2] in APPROVED_FEATURES:
        return parts[2]
    return None


def _module_name(path: Path) -> str:
    relative = path.relative_to(SOURCE_ROOT).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(("dryv", *parts))


def _relative(path: Path) -> str:
    return path.relative_to(SOURCE_ROOT).as_posix()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
