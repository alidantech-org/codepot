from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).parents[2] / "src" / "codepotg_language_dart"
PACKAGE_ROOT = ROOT.parents[2]
FORBIDDEN_IMPORTS = (
    "codepotg.application",
    "codepotg.cli",
    "codepotg.domain",
    "codepotg.infrastructure",
    "codepotg.runtime",
    "codepotg_language_typescript",
    "codepotg_openapi",
    "codepotg_pack",
    "jinja",
    "requests",
    "socket",
    "subprocess",
)
FORBIDDEN_RUNTIME_CALLS = {
    "open",
    "getenv",
    "system",
    "popen",
    "resolve",
    "exists",
    "stat",
}


def _runtime_files() -> tuple[Path, ...]:
    return tuple(sorted(ROOT.rglob("*.py")))


def test_runtime_imports_only_public_contracts() -> None:
    for path in _runtime_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                assert not name.startswith(FORBIDDEN_IMPORTS), (path, name)


def test_no_ordinary_filesystem_environment_network_or_process_calls() -> None:
    for path in _runtime_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            if isinstance(function, ast.Name):
                assert function.id not in FORBIDDEN_RUNTIME_CALLS, (path, function.id)
            elif isinstance(function, ast.Attribute):
                assert function.attr not in FORBIDDEN_RUNTIME_CALLS, (path, function.attr)


def test_no_mutable_module_level_registry_or_cache() -> None:
    for path in _runtime_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                targets = node.targets if isinstance(node, ast.Assign) else (node.target,)
                names = {target.id for target in targets if isinstance(target, ast.Name)}
                if names == {"__all__"}:
                    continue
                assert not isinstance(value, (ast.Dict, ast.List, ast.Set)), path


def test_no_renderer_framework_or_github_files() -> None:
    runtime = "\n".join(path.read_text(encoding="utf-8") for path in _runtime_files())
    for token in (
        "TypeRenderer",
        "LiteralRenderer",
        "CommentRenderer",
        "ImportRenderer",
        "ExportRenderer",
        "SemanticExtension",
        "Flutter",
        "Riverpod",
        "Bloc",
        "GoRouter",
        "pubspec.yaml",
        "build_runner",
        "os.environ",
    ):
        assert token not in runtime
    assert not list(PACKAGE_ROOT.rglob(".github"))


def test_no_same_name_module_package_collision() -> None:
    directory_names = {path.name for path in ROOT.rglob("*") if path.is_dir()}
    module_names = {path.stem for path in ROOT.rglob("*.py")}
    assert not (directory_names & module_names)
