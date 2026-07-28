from __future__ import annotations

from pathlib import PurePosixPath

from dryv.api import CancellationToken
from dryv.diagnostics import Diagnostics
from dryv.ir import Contract
from dryv.plugins import PluginCategory, PluginDescriptor
from dryv.ports import (
    IdentifierRole,
    IdentifierValidationRequest,
    ModulePathFacts,
    ModulePathKind,
    ModulePathRequest,
    OutputPathValidationRequest,
    RenderRequest,
    RenderResult,
    SourceAdapter,
    SourceAdapterRequest,
    SourceAdapterResult,
    TargetAdapter,
    TargetDescriptor,
    TemplateEngine,
)
from dryv.testing import (
    assert_source_adapter_conformance,
    assert_target_adapter_conformance,
    assert_template_engine_conformance,
)
from dryv.versions import (
    IR_API_VERSION,
    PLUGIN_API_VERSION,
    BehaviorVersion,
    Version,
)


def descriptor(category: PluginCategory, plugin_id: str) -> PluginDescriptor:
    return PluginDescriptor(
        id=plugin_id,
        category=category,
        distribution=f"test-{plugin_id}",
        version=Version.parse("1.0.0"),
        api_version=PLUGIN_API_VERSION,
        ir_version=IR_API_VERSION,
        capabilities=("deterministic",),
    )


class FakeSourceAdapter:
    def __init__(self, contract: Contract) -> None:
        self._contract = contract
        self._plugin = descriptor(PluginCategory.SOURCE_ADAPTER, "test_source")

    @property
    def plugin(self) -> PluginDescriptor:
        return self._plugin

    def normalize(
        self,
        request: SourceAdapterRequest,
        cancellation: CancellationToken,
    ) -> SourceAdapterResult:
        cancellation.raise_if_cancelled()
        return SourceAdapterResult(
            contract=self._contract,
            digest=f"sha256:{request.source_id}:stable",
        )


class FakeTargetAdapter:
    def __init__(self) -> None:
        self._plugin = descriptor(PluginCategory.TARGET_ADAPTER, "test_target")
        self._targets = (
            TargetDescriptor(
                id="test",
                aliases=(),
                extensions=(".test",),
                behavior_version=BehaviorVersion(1),
                capabilities=("module.relative",),
            ),
        )

    @property
    def plugin(self) -> PluginDescriptor:
        return self._plugin

    @property
    def targets(self) -> tuple[TargetDescriptor, ...]:
        return self._targets

    def validate_identifier(self, request: IdentifierValidationRequest) -> Diagnostics:
        return Diagnostics()

    def validate_output_path(self, request: OutputPathValidationRequest) -> Diagnostics:
        return Diagnostics()

    def resolve_module_path(self, request: ModulePathRequest) -> ModulePathFacts:
        assert request.provider_artifact is not None
        current_parent = PurePosixPath(request.current_artifact).parent
        provider = PurePosixPath(request.provider_artifact)
        relative = (
            PurePosixPath("..", provider.name)
            if current_parent != provider.parent
            else PurePosixPath(provider.name)
        )
        return ModulePathFacts(
            kind=ModulePathKind.RELATIVE,
            specifier=relative.as_posix(),
            current_artifact=request.current_artifact,
            provider_artifact=request.provider_artifact,
            relative_path=relative.as_posix(),
        )


class FakeTemplateEngine:
    def __init__(self) -> None:
        self._plugin = descriptor(PluginCategory.TEMPLATE_ENGINE, "test_engine")

    @property
    def plugin(self) -> PluginDescriptor:
        return self._plugin

    @property
    def suffixes(self) -> tuple[str, ...]:
        return (".testtpl",)

    def render(
        self,
        request: RenderRequest,
        cancellation: CancellationToken,
    ) -> RenderResult:
        cancellation.raise_if_cancelled()
        output = request.source
        for key, value in request.context:
            output = output.replace("{{ " + key + " }}", str(value))
        return RenderResult(content=output)


def test_adapter_protocols_and_public_conformance_helpers(
    connected_contract: Contract,
) -> None:
    source = FakeSourceAdapter(connected_contract)
    target = FakeTargetAdapter()
    engine = FakeTemplateEngine()

    assert isinstance(source, SourceAdapter)
    assert isinstance(target, TargetAdapter)
    assert isinstance(engine, TemplateEngine)

    assert_source_adapter_conformance(
        source,
        SourceAdapterRequest(source_id="fixture", content="contract"),
    )
    assert_target_adapter_conformance(
        target,
        identifier=IdentifierValidationRequest("User", IdentifierRole.TYPE),
        output_path=OutputPathValidationRequest("src/user.test", "test"),
        module_path=ModulePathRequest(
            current_artifact="src/services/users.test",
            provider_artifact="src/types/user.test",
        ),
    )
    assert_template_engine_conformance(
        engine,
        RenderRequest(
            template_id="hello",
            source="Hello {{ name }}",
            context=(("name", "Codepot"),),
        ),
    )
