from dryv.ports import (
    IdentifierRole,
    IdentifierValidationRequest,
    ModulePathRequest,
    OutputPathValidationRequest,
    TargetAdapter,
)
from dryv.testing import assert_target_adapter_conformance

from dryv_language_dart import DartTargetAdapter


def test_public_target_conformance_and_isolation() -> None:
    adapter = DartTargetAdapter()
    assert isinstance(adapter, TargetAdapter)
    assert_target_adapter_conformance(
        adapter,
        identifier=IdentifierValidationRequest("User", IdentifierRole.TYPE),
        output_path=OutputPathValidationRequest("lib/src/user.dart", "dart"),
        module_path=ModulePathRequest(
            "lib/src/service.dart",
            provider_artifact="lib/src/user.dart",
        ),
    )
    assert DartTargetAdapter().targets == DartTargetAdapter().targets
