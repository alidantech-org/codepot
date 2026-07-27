from __future__ import annotations

import string
from pathlib import Path

from codepotg.ports import (
    IdentifierRole,
    IdentifierValidationRequest,
    ModulePathRequest,
    OutputPathValidationRequest,
)
from codepotg_language_dart import DartTargetAdapter


def test_ascii_candidate_matrix_never_crashes_and_is_deterministic() -> None:
    adapter = DartTargetAdapter()
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


def test_path_depth_matrix_is_stable() -> None:
    adapter = DartTargetAdapter()
    for depth in range(1, 40):
        prefix = "/".join(f"segment{index}" for index in range(depth))
        request = OutputPathValidationRequest(f"{prefix}/value.dart", "dart")
        assert adapter.validate_output_path(request) == adapter.validate_output_path(
            request
        )


def test_relative_depth_uses_only_posix_separators() -> None:
    adapter = DartTargetAdapter()
    for depth in range(1, 30):
        current = "/".join(("lib", *(f"c{index}" for index in range(depth)), "a.dart"))
        provider = "lib/shared/user.dart"
        facts = adapter.resolve_module_path(
            ModulePathRequest(current, provider_artifact=provider)
        )
        assert "\\" not in facts.specifier
        assert facts.specifier.endswith("user.dart")


def test_results_do_not_depend_on_current_working_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    adapter = DartTargetAdapter()
    request = ModulePathRequest(
        "lib/src/features/service.dart",
        provider_artifact="lib/src/types/user.dart",
    )
    before = adapter.resolve_module_path(request)
    monkeypatch.chdir(tmp_path)
    assert adapter.resolve_module_path(request) == before
