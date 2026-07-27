from codepotg.ports import (
    IdentifierRole,
    IdentifierValidationRequest,
    ModulePathRequest,
    OutputPathValidationRequest,
    TargetAdapter,
)
from codepotg.testing import assert_target_adapter_conformance

from codepotg_language_typescript import TypeScriptTargetAdapter


def test_public_target_conformance_and_isolation() -> None:
    adapter = TypeScriptTargetAdapter()
    assert isinstance(adapter, TargetAdapter)
    assert_target_adapter_conformance(
        adapter,
        identifier=IdentifierValidationRequest("User", IdentifierRole.TYPE),
        output_path=OutputPathValidationRequest("src/user.ts", "typescript"),
        module_path=ModulePathRequest(
            "src/service.ts",
            provider_artifact="src/user.ts",
        ),
    )
    assert TypeScriptTargetAdapter().targets == TypeScriptTargetAdapter().targets
