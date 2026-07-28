from __future__ import annotations

import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[2]
SOURCE_ROOT = PACKAGE_ROOT / "src" / "dryv_cli"

REQUIRED_PACKAGES = {"commands", "presentation", "prompts", "services"}
FORBIDDEN_IMPORT_PREFIXES = (
    "dryv.application",
    "dryv.domain",
    "dryv.infrastructure",
    "dryv.runtime.plugins",
)


def test_cli_has_clean_subsystem_directories_without_placeholders() -> None:
    present = {
        path.name
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir() and (path / "__init__.py").exists()
    }

    assert present >= REQUIRED_PACKAGES
    assert not tuple(PACKAGE_ROOT.rglob(".gitkeep"))


def test_cli_consumes_only_public_dryv_contracts() -> None:
    violations: list[tuple[Path, str]] = []
    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        for imported in _absolute_imports(path):
            if imported.startswith(FORBIDDEN_IMPORT_PREFIXES):
                violations.append((path.relative_to(SOURCE_ROOT), imported))

    assert violations == []


def test_cli_uses_no_direct_python_terminal_io() -> None:
    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        assert not ({"print", "input"} & _direct_call_names(path)), path


def test_cli_avoids_box_and_panel_rendering() -> None:
    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        assert "rich.panel" not in source
        assert "Panel(" not in source
        assert "box=" not in source
        assert "ROUNDED" not in source
        assert "DOUBLE" not in source


def test_cli_package_owns_the_console_script() -> None:
    project = (PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert '[project.scripts]' in project
    assert 'dryv = "dryv_cli.main:main"' in project
    assert '"rich>=' in project
    assert '"questionary>=' in project
    assert '"click>=' in project


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
