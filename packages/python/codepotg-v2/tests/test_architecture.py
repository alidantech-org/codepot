from __future__ import annotations

import ast
import importlib
import tomllib
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1]
SOURCE_ROOT = PACKAGE_ROOT / "src" / "codepotg"

FORBIDDEN_TOP_LEVEL_IMPORTS = {
    "app",
    "cli",
    "codepot_file",
    "constants",
    "contracts",
    "emission",
    "inference",
    "languages",
    "openapi",
}
FORBIDDEN_PLUGIN_IMPLEMENTATIONS = {
    "codepotg_openapi",
    "jinja2",
    "typescript",
    "dart",
}


def test_package_metadata_is_isolated_and_dependency_free() -> None:
    project = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]

    assert project["name"] == "codepotg-core"
    assert project["requires-python"] == ">=3.11"
    assert project["dependencies"] == []


def test_public_namespaces_import_without_discovery_or_optional_plugins() -> None:
    modules = (
        "codepotg",
        "codepotg.api",
        "codepotg.core",
        "codepotg.diagnostics",
        "codepotg.ir",
        "codepotg.naming",
        "codepotg.plugins",
        "codepotg.ports",
        "codepotg.testing",
        "codepotg.validation",
        "codepotg.versions",
    )

    for module in modules:
        assert importlib.import_module(module)


def test_core_has_no_old_runtime_or_plugin_implementation_imports() -> None:
    violations: list[str] = []

    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = tuple(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = (node.module,)
            else:
                continue

            for name in names:
                root = name.split(".", 1)[0]
                if root in FORBIDDEN_TOP_LEVEL_IMPORTS | FORBIDDEN_PLUGIN_IMPLEMENTATIONS:
                    violations.append(f"{path.relative_to(PACKAGE_ROOT)} imports {name}")

    assert violations == []


def test_no_github_automation_is_added_to_v2_package() -> None:
    assert not (PACKAGE_ROOT / ".github").exists()
