import time

import pytest
from codepotg.ports import IdentifierRole, IdentifierValidationRequest, ModulePathRequest
from codepotg_language_dart import DartTargetAdapter


@pytest.mark.performance
def test_deterministic_large_batch() -> None:
    adapter = DartTargetAdapter()
    start = time.perf_counter()
    for index in range(10_000):
        adapter.validate_identifier(
            IdentifierValidationRequest(f"User{index}", IdentifierRole.TYPE)
        )
        adapter.resolve_module_path(
            ModulePathRequest(
                "lib/src/service.dart",
                provider_artifact=f"lib/src/types/user_{index}.dart",
            )
        )
    assert time.perf_counter() - start < 10
