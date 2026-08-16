from __future__ import annotations

import ast
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).parents[5]
DRYV_ROOT = REPO_ROOT / "packages" / "python" / "dryv"
API_ROOT = REPO_ROOT / "packages" / "python" / "dryv-api"
CLI_ROOT = REPO_ROOT / "packages" / "python" / "dryv-cli"
AUTHOR_ROOT = REPO_ROOT / "packages" / "python" / "dryv-author"
JINJA_ROOT = REPO_ROOT / "packages" / "python" / "dryv-template-jinja"
HANDLEBARS_CLIENT = (
    REPO_ROOT
    / "packages"
    / "nodejs"
    / "codepotx"
    / "render-clients"
    / "handlebars"
    / "stdio.mjs"
)
TYPE_SCRIPT_CLIENT = REPO_ROOT / "packages" / "nodejs" / "dryv-client" / "src" / "index.ts"


def test_cli_project_client_does_not_import_dryv_engine() -> None:
    violations = _python_import_violations(CLI_ROOT / "src", forbidden=("dryv",))
    assert violations == []
    project_client = (CLI_ROOT / "src" / "dryv_cli" / "project_client.py").read_text(encoding="utf-8")
    assert "applyComplete" in project_client
    assert "expectedPreviousHash" in project_client


def test_jinja_render_client_has_no_dryv_dependency_or_plugin_entry_point() -> None:
    violations = _python_import_violations(JINJA_ROOT / "src", forbidden=("dryv",))
    assert violations == []
    project = tomllib.loads((JINJA_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = tuple(project["project"].get("dependencies", ()))
    assert all(not str(item).lower().startswith("dryv") for item in dependencies)
    assert "entry-points" not in project["project"]
    assert (JINJA_ROOT / "src" / "dryv_template_jinja" / "session.py").is_file()
    assert not (JINJA_ROOT / "src" / "dryv_template_jinja" / "plugin.py").exists()


def test_python_author_backend_never_imports_runtime_generation_features() -> None:
    forbidden = (
        "dryv.runtime",
        "dryv.features",
        "dryv.generation",
        "dryv.plugins",
        "dryv.ports",
    )
    assert _python_import_violations(AUTHOR_ROOT / "src", forbidden=forbidden) == []
    assert (AUTHOR_ROOT / "src" / "dryv_author" / "stdio.py").is_file()


def test_api_is_outer_runtime_host_not_project_filesystem_owner() -> None:
    service = (API_ROOT / "src" / "dryv_api" / "service.py").read_text(encoding="utf-8")
    assert "DryvRuntime" in service
    assert "renderComplete" in service
    assert "applyComplete" not in service
    for path in (API_ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "ManagedFilesystemWriter" not in text
        assert "generate_to_files" not in text


def test_handlebars_render_client_is_process_isolated_and_has_no_dryv_or_codegen_imports() -> None:
    text = HANDLEBARS_CLIENT.read_text(encoding="utf-8")
    assert "from 'handlebars'" in text
    assert "dryv" not in text.lower()
    assert "codepotx" not in text.lower()
    assert "../" not in text
    assert "handlebars/v1" in text


def test_typescript_client_is_transport_contract_only() -> None:
    text = TYPE_SCRIPT_CLIENT.read_text(encoding="utf-8")
    assert 'DRYV_API_VERSION = "dryv.api/v1"' in text
    assert "interface DryvTransport" in text
    assert "dryv.runtime" not in text
    assert "node:fs" not in text
    assert "applyComplete" not in text


def test_active_package_docs_do_not_advertise_removed_plugin_or_writer_architecture() -> None:
    documents = (
        DRYV_ROOT / "README.md",
        API_ROOT / "README.md",
        CLI_ROOT / "README.md",
        AUTHOR_ROOT / "README.md",
    )
    forbidden = (
        "dryv.template_engines",
        "dryv.source_adapters",
        "RuntimePlugins",
        "generate_to_files",
    )
    violations: list[str] = []
    for path in documents:
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                violations.append(f"{path.relative_to(REPO_ROOT)} advertises {token}")
    assert violations == []


def _python_import_violations(root: Path, *, forbidden: tuple[str, ...]) -> list[str]:
    violations: list[str] = []
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = tuple(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                modules = (node.module,)
            else:
                continue
            for module in modules:
                if any(module == item or module.startswith(f"{item}.") for item in forbidden):
                    violations.append(f"{path.relative_to(REPO_ROOT)} imports {module}")
    return violations
