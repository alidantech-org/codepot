import time

import pytest
from codepotg.ports import IdentifierRole, IdentifierValidationRequest, ModulePathRequest
from codepotg_language_typescript import TypeScriptTargetAdapter


@pytest.mark.performance
def test_deterministic_large_batch() -> None:
    adapter = TypeScriptTargetAdapter()
    start = time.perf_counter()
    for index in range(10_000):
        adapter.validate_identifier(
            IdentifierValidationRequest(f"User{index}", IdentifierRole.TYPE)
        )
        adapter.resolve_module_path(
            ModulePathRequest(
                "src/service.ts",
                provider_artifact=f"src/types/user{index}.ts",
            )
        )
    assert time.perf_counter() - start < 10
