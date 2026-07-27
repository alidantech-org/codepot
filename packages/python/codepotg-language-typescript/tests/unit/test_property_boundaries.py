from __future__ import annotations

import string
from pathlib import Path

from codepotg.ports import (
    IdentifierRole,
    IdentifierValidationRequest,
    ModulePathRequest,
    OutputPathValidationRequest,
)

from codepotg_language_typescript import (
    AliasBinding,
    TypeScriptTargetAdapter,
    TypeScriptTargetOptions,
)


def test_ascii_candidate_matrix_never_crashes_and_is_deterministic() -> None:
    adapter = TypeScriptTargetAdapter()
    candidates = [
        "",
        *(character + "tail" for character in string.printable),
        *("a" + character for character in string.printable),
        "a" * 4096,
    ]
    for role in IdentifierRole:
        for value in candidates:
            request = IdentifierValidationRequest(value, role)
            first = adapter.validate_identifier(request)
            assert first == adapter.validate_identifier(request)
            assert request.value == value


def test_path_depth_and_extension_matrix_is_stable() -> None:
    adapter = TypeScriptTargetAdapter()
    suffixes = (".ts", ".tsx", ".mts", ".cts", ".d.ts", ".d.mts", ".d.cts")
    for depth in range(1, 40):
        prefix = "/".join(f"segment{index}" for index in range(depth))
        for suffix in suffixes:
            target = "typescript-jsx" if suffix == ".tsx" else "typescript"
            request = OutputPathValidationRequest(f"{prefix}/value{suffix}", target)
            assert adapter.validate_output_path(request) == adapter.validate_output_path(request)


def test_alias_segment_boundaries_and_relative_depth() -> None:
    adapter = TypeScriptTargetAdapter(
        TypeScriptTargetOptions(
            aliases=(
                AliasBinding("@", "src"),
                AliasBinding("@domain", "src/domain"),
            )
        )
    )
    nested = adapter.resolve_module_path(
        ModulePathRequest(
            "src/consumer.ts",
            provider_artifact="src/domain/model/user.ts",
        )
    )
    adjacent = adapter.resolve_module_path(
        ModulePathRequest(
            "src/consumer.ts",
            provider_artifact="src/domainish/user.ts",
        )
    )
    assert nested.specifier == "@domain/model/user"
    assert adjacent.specifier == "@/domainish/user"


def test_results_do_not_depend_on_current_working_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    adapter = TypeScriptTargetAdapter()
    request = ModulePathRequest(
        "src/features/service.ts",
        provider_artifact="src/types/user.ts",
    )
    before = adapter.resolve_module_path(request)
    monkeypatch.chdir(tmp_path)
    assert adapter.resolve_module_path(request) == before
