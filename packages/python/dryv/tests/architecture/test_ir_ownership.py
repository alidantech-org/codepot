from __future__ import annotations

import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[2]
SOURCE_ROOT = PACKAGE_ROOT / "src" / "dryv"
CANONICAL_ROOT = SOURCE_ROOT / "ir"
LEGACY_ROOT = SOURCE_ROOT / "domain" / "ir"

CONCEPT_ROOTS = {
    "contract", "cross_cutting", "events", "failures", "groups", "kernel",
    "operations", "policies", "presentations", "properties", "schemas",
    "sources", "storage", "validation", "views", "workflows",
}


def test_canonical_ir_exposes_the_approved_concept_roots() -> None:
    present = {path.name for path in CANONICAL_ROOT.iterdir() if path.is_dir()}
    assert CONCEPT_ROOTS <= present


def test_legacy_ir_contains_no_semantic_class_definitions() -> None:
    violations: list[str] = []
    for path in sorted(LEGACY_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if any(isinstance(node, ast.ClassDef) for node in ast.walk(tree)):
            violations.append(str(path.relative_to(SOURCE_ROOT)))
    assert violations == []


def test_production_code_uses_canonical_ir_imports() -> None:
    violations: list[str] = []
    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        relative = path.relative_to(SOURCE_ROOT).as_posix()
        if relative.startswith("domain/ir/"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module == "dryv.domain.ir" or node.module.startswith("dryv.domain.ir."):
                    violations.append(f"{relative}: {node.module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "dryv.domain.ir" or alias.name.startswith("dryv.domain.ir."):
                        violations.append(f"{relative}: {alias.name}")
    assert violations == []


def test_canonical_ir_never_depends_on_features() -> None:
    violations: list[str] = []
    for path in sorted(CANONICAL_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            for module in modules:
                if module == "dryv.features" or module.startswith("dryv.features."):
                    violations.append(f"{path.relative_to(SOURCE_ROOT)}: {module}")
    assert violations == []
