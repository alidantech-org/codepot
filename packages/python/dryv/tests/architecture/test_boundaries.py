from __future__ import annotations

import ast
import importlib
import re
import tomllib
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[2]
REPO_ROOT = PACKAGE_ROOT.parents[2]
SOURCE_ROOT = PACKAGE_ROOT / "src" / "dryv"
FEATURE_ROOT = SOURCE_ROOT / "features"
TASK_ROOT = REPO_ROOT / ".docs" / "packages" / "python" / "dryv" / "tasks"

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

ACTIVE_TOP_LEVEL_PACKAGES = {"features", "ir", "runtime"}

# These packages belong to the pre-Feature architecture and may remain only
# during the bounded migration window. Task 21 removes or migrates the
# obsolete runtime/application/infrastructure/plugin/port ownership once the
# replacement path is complete.
LEGACY_TOP_LEVEL_EXEMPTIONS = {
    "api": "21-remove-legacy-runtime-paths.md",
    "application": "21-remove-legacy-runtime-paths.md",
    "config": "21-remove-legacy-runtime-paths.md",
    "diagnostics": "21-remove-legacy-runtime-paths.md",
    "domain": "21-remove-legacy-runtime-paths.md",
    "generation": "21-remove-legacy-runtime-paths.md",
    "infrastructure": "21-remove-legacy-runtime-paths.md",
    "plugins": "21-remove-legacy-runtime-paths.md",
    "ports": "21-remove-legacy-runtime-paths.md",
    "testing": "21-remove-legacy-runtime-paths.md",
    "versions": "21-remove-legacy-runtime-paths.md",
}

LEGACY_PROJECT_WRITE_EXEMPTIONS = {
    "application/write.py": "21-remove-legacy-runtime-paths.md",
    "infrastructure/writers.py": "21-remove-legacy-runtime-paths.md",
}

FORBIDDEN_VAGUE_DIRECTORIES = {"common", "helpers", "misc", "shared", "utils"}

SERVER_DEPENDENCIES = {
    "aiohttp",
    "django",
    "fastapi",
    "flask",
    "hypercorn",
    "sanic",
    "starlette",
    "tornado",
    "uvicorn",
    "websockets",
}

SERVER_IMPORT_PREFIXES = (
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


def test_feature_catalog_is_exact_and_each_feature_has_a_public_root() -> None:
    present = {
        path.name
        for path in FEATURE_ROOT.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    }

    assert present == APPROVED_FEATURES
    assert (FEATURE_ROOT / "__init__.py").is_file()

    for feature in sorted(APPROVED_FEATURES):
        assert importlib.import_module(f"dryv.features.{feature}")


def test_only_approved_active_or_explicit_legacy_top_level_packages_exist() -> None:
    present = {
        path.name
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    }
    allowed = ACTIVE_TOP_LEVEL_PACKAGES | set(LEGACY_TOP_LEVEL_EXEMPTIONS)

    assert present - allowed == set()


def test_every_legacy_exception_names_a_real_follow_up_task() -> None:
    exemptions = {
        **LEGACY_TOP_LEVEL_EXEMPTIONS,
        **LEGACY_PROJECT_WRITE_EXEMPTIONS,
    }

    assert exemptions
    for subject, task in exemptions.items():
        assert re.fullmatch(r"\d{2}-.+\.md", task), subject
        assert (TASK_ROOT / task).is_file(), f"{subject} points to missing {task}"


def test_features_do_not_import_runtime_or_sibling_features() -> None:
    violations: list[str] = []

    for feature in sorted(APPROVED_FEATURES):
        feature_dir = FEATURE_ROOT / feature
        for path in sorted(feature_dir.rglob("*.py")):
            for imported in _imported_modules(path):
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

    for path in sorted((SOURCE_ROOT / "ir").rglob("*.py")):
        for imported in _imported_modules(path):
            if imported == "dryv.runtime" or imported.startswith("dryv.runtime."):
                violations.append(f"{_relative(path)} imports Runtime: {imported}")
            if imported == "dryv.features" or imported.startswith("dryv.features."):
                violations.append(f"{_relative(path)} imports Features: {imported}")

    assert violations == []


def test_production_consumers_use_feature_public_roots_only() -> None:
    violations: list[str] = []

    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        if _is_inside(path, FEATURE_ROOT):
            continue
        for node in ast.walk(_tree(path)):
            module = _feature_import_module(node)
            if module is None:
                continue
            parts = module.split(".")
            if len(parts) > 3:
                violations.append(
                    f"{_relative(path)} imports Feature internal path: {module}"
                )

    assert violations == []


def test_runtime_is_the_only_owner_allowed_to_coordinate_multiple_features() -> None:
    violations: list[str] = []
    runtime_root = SOURCE_ROOT / "runtime"

    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        if _is_inside(path, runtime_root) or _is_inside(path, FEATURE_ROOT):
            continue
        used_features = {
            feature
            for feature in (_feature_name(module) for module in _imported_modules(path))
            if feature is not None
        }
        if len(used_features) > 1:
            violations.append(
                f"{_relative(path)} coordinates multiple Features: "
                f"{', '.join(sorted(used_features))}"
            )

    assert violations == []


def test_vague_feature_directories_are_rejected() -> None:
    vague = {
        path.relative_to(FEATURE_ROOT).as_posix()
        for path in FEATURE_ROOT.rglob("*")
        if path.is_dir() and path.name in FORBIDDEN_VAGUE_DIRECTORIES
    }

    assert vague == set()


def test_dryv_does_not_add_server_hosting_dependencies_or_imports() -> None:
    project = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = {
        _dependency_name(item)
        for item in project.get("project", {}).get("dependencies", [])
    }
    assert dependencies.isdisjoint(SERVER_DEPENDENCIES)

    violations: list[str] = []
    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        for imported in _imported_modules(path):
            if imported.startswith(SERVER_IMPORT_PREFIXES):
                violations.append(f"{_relative(path)} imports server host {imported}")

    assert violations == []


def test_legacy_project_write_ownership_is_explicitly_task_bound() -> None:
    # Task 00 does not remove the current writer path. The known
    # engine-side project-write ownership remains an explicit, temporary
    # exception until Task 21 removes the legacy implementation.
    for relative, task in LEGACY_PROJECT_WRITE_EXEMPTIONS.items():
        assert (SOURCE_ROOT / relative).is_file(), relative
        assert task == "21-remove-legacy-runtime-paths.md"


def _tree(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imported_modules(path: Path) -> tuple[str, ...]:
    module_name = _module_name(path)
    package_name = module_name if path.name == "__init__.py" else module_name.rsplit(".", 1)[0]
    imports: list[str] = []

    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
            continue
        if not isinstance(node, ast.ImportFrom):
            continue

        if node.level == 0:
            if node.module:
                imports.append(node.module)
                if node.module == "dryv.features":
                    imports.extend(
                        f"dryv.features.{alias.name}"
                        for alias in node.names
                        if alias.name in APPROVED_FEATURES
                    )
            continue

        package_parts = package_name.split(".")
        ascend = node.level - 1
        if ascend > len(package_parts):
            continue
        base_parts = package_parts[: len(package_parts) - ascend]
        if node.module:
            imports.append(".".join((*base_parts, node.module)))
        else:
            imports.extend(".".join((*base_parts, alias.name)) for alias in node.names)

    return tuple(imports)


def _feature_import_module(node: ast.AST) -> str | None:
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name.startswith("dryv.features."):
                return alias.name
        return None

    if not isinstance(node, ast.ImportFrom) or node.level != 0 or node.module is None:
        return None
    if node.module == "dryv.features":
        return node.module
    if node.module.startswith("dryv.features."):
        return node.module
    return None


def _feature_name(module: str) -> str | None:
    parts = module.split(".")
    if len(parts) < 3 or parts[:2] != ["dryv", "features"]:
        return None
    return parts[2] if parts[2] in APPROVED_FEATURES else None


def _module_name(path: Path) -> str:
    relative = path.relative_to(SOURCE_ROOT).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(("dryv", *parts))


def _dependency_name(requirement: str) -> str:
    return re.split(r"[\s\[<>=!~;]", requirement, maxsplit=1)[0].lower().replace("_", "-")


def _relative(path: Path) -> str:
    return path.relative_to(SOURCE_ROOT).as_posix()


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
