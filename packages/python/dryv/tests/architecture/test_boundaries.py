from __future__ import annotations

import ast
import importlib
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[2]
SOURCE_ROOT = PACKAGE_ROOT / "src" / "dryv"
TEST_ROOT = PACKAGE_ROOT / "tests"

REQUIRED_PACKAGES = {
    "api",
    "application",
    "config",
    "diagnostics",
    "domain",
    "generation",
    "infrastructure",
    "ir",
    "plugins",
    "ports",
    "runtime",
    "testing",
    "versions",
}
REQUIRED_TEST_AREAS = {
    "architecture",
    "contracts",
    "distribution",
    "fixtures",
    "unit",
}
FORBIDDEN_FLAT_MODULES = {
    "api.py",
    "core.py",
    "diagnostics.py",
    "ir.py",
    "naming.py",
    "plugins.py",
    "ports.py",
    "selectors.py",
    "testing.py",
    "validation.py",
    "versions.py",
}
FORBIDDEN_OLD_IMPORT_ROOTS = {
    "app",
    "codepot_file",
    "constants",
    "contracts",
    "emission",
    "inference",
    "languages",
}


def test_planned_package_structure_is_present_without_flat_dump_modules() -> None:
    present_packages = {
        path.name
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir() and (path / "__init__.py").exists()
    }

    assert present_packages >= REQUIRED_PACKAGES
    assert not {path.name for path in SOURCE_ROOT.iterdir()} & FORBIDDEN_FLAT_MODULES
    assert (SOURCE_ROOT / "domain" / "ir").is_dir()
    assert (SOURCE_ROOT / "domain" / "generation").is_dir()


def test_tests_mirror_subsystem_boundaries_instead_of_flat_test_files() -> None:
    present_areas = {path.name for path in TEST_ROOT.iterdir() if path.is_dir()}
    flat_tests = tuple(TEST_ROOT.glob("test_*.py"))

    assert present_areas >= REQUIRED_TEST_AREAS
    assert flat_tests == ()
    assert (TEST_ROOT / "unit" / "domain" / "ir").is_dir()
    assert (TEST_ROOT / "unit" / "domain" / "generation").is_dir()
    assert (TEST_ROOT / "contracts" / "ports").is_dir()


def test_public_namespaces_import_without_discovery_or_optional_plugins() -> None:
    modules = (
        "dryv",
        "dryv.api",
        "dryv.config",
        "dryv.diagnostics",
        "dryv.generation",
        "dryv.ir",
        "dryv.plugins",
        "dryv.ports",
        "dryv.runtime",
        "dryv.testing",
        "dryv.versions",
    )

    for module in modules:
        assert importlib.import_module(module)


def test_domain_dependency_direction_and_clean_room_boundary() -> None:
    violations: list[str] = []

    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        relative = path.relative_to(SOURCE_ROOT)
        imports = _absolute_imports(path)
        for imported in imports:
            root = imported.split(".", 1)[0]
            if root in FORBIDDEN_OLD_IMPORT_ROOTS:
                violations.append(f"{relative} imports old/plugin implementation {imported}")
            if relative.parts[0] == "domain" and imported.startswith(
                (
                    "dryv.application",
                    "dryv.infrastructure",
                    "dryv.runtime",
                )
            ):
                violations.append(f"{relative} violates domain dependency direction: {imported}")
            if relative.parts[0] == "application" and imported.startswith(
                "dryv.infrastructure"
            ):
                violations.append(f"{relative} imports concrete infrastructure: {imported}")

    assert violations == []


def test_core_has_no_terminal_frontend_or_console_script() -> None:
    assert not (SOURCE_ROOT / "cli").exists()

    project = (PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "[project.scripts]" not in project
    assert "rich" not in project.lower()
    assert "questionary" not in project.lower()
    assert "typer" not in project.lower()

    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        imports = _absolute_imports(path)
        assert "argparse" not in imports
        assert "click" not in imports
        assert "rich" not in imports
        assert "questionary" not in imports
        assert not ({"print", "input"} & _direct_call_names(path))


def test_no_same_name_module_and_package_collisions() -> None:
    collisions = {
        path.stem
        for path in SOURCE_ROOT.glob("*.py")
        if path.stem != "__init__" and (SOURCE_ROOT / path.stem).is_dir()
    }
    assert collisions == set()


def test_no_github_automation_is_added_to_v2_package() -> None:
    assert not (PACKAGE_ROOT / ".github").exists()


def _absolute_imports(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imports.append(node.module)
    return tuple(imports)


def _direct_call_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
