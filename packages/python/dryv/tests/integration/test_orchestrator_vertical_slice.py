from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from dryv.api import CancellationToken
from dryv.application import generate
from dryv.diagnostics import Diagnostics
from dryv.ir import (
    Contract,
    Group,
    Name,
    Schema,
    SchemaKind,
    SemanticId,
)
from dryv.plugins import PluginCategory, PluginDescriptor, PluginTrust
from dryv.ports import (
    IdentifierValidationRequest,
    ModulePathFacts,
    ModulePathKind,
    ModulePathRequest,
    OutputPathValidationRequest,
    RenderRequest,
    RenderResult,
    SourceAdapterRequest,
    SourceAdapterResult,
    TargetDescriptor,
)
from dryv.runtime import RuntimePlugins
from dryv.versions import IR_API_VERSION, PLUGIN_API_VERSION, BehaviorVersion, Version


def _plugin(identifier: str, category: PluginCategory) -> PluginDescriptor:
    return PluginDescriptor(
        id=identifier,
        category=category,
        distribution="orchestrator-test",
        version=Version.parse("1.0.0"),
        api_version=PLUGIN_API_VERSION,
        ir_version=IR_API_VERSION,
        trust=PluginTrust.EXECUTABLE,
    )


@dataclass(frozen=True, slots=True)
class FakeSource:
    plugin: PluginDescriptor = _plugin("fake-source", PluginCategory.SOURCE_ADAPTER)

    def normalize(
        self,
        request: SourceAdapterRequest,
        cancellation: CancellationToken,
    ) -> SourceAdapterResult:
        cancellation.raise_if_cancelled()
        schema = Schema(
            id=SemanticId("users.schema"),
            name=Name("User"),
            kind=SchemaKind.OBJECT,
        )
        contract = Contract(
            id=SemanticId("example.contract"),
            name=Name("Example"),
            groups=(
                Group(
                    id=SemanticId("users.group"),
                    name=Name("Users"),
                    schemas=(schema,),
                ),
            ),
        )
        return SourceAdapterResult(contract, "fake-digest")


@dataclass(frozen=True, slots=True)
class FakeTarget:
    plugin: PluginDescriptor = _plugin("fake-target", PluginCategory.TARGET_ADAPTER)
    targets: tuple[TargetDescriptor, ...] = (
        TargetDescriptor(
            id="fake-ts",
            aliases=(),
            extensions=(".ts",),
            behavior_version=BehaviorVersion(1),
            capabilities=("module.relative_path",),
        ),
    )

    def validate_identifier(self, request: IdentifierValidationRequest) -> Diagnostics:
        return Diagnostics()

    def validate_output_path(self, request: OutputPathValidationRequest) -> Diagnostics:
        return Diagnostics()

    def resolve_module_path(self, request: ModulePathRequest) -> ModulePathFacts:
        assert request.provider_artifact is not None
        current = PurePosixPath(request.current_artifact)
        provider = PurePosixPath(request.provider_artifact)
        current_parent = current.parent.parts
        provider_parts = provider.parts
        common = 0
        for left, right in zip(current_parent, provider_parts, strict=False):
            if left != right:
                break
            common += 1
        parts = ("..",) * (len(current_parent) - common) + provider_parts[common:]
        value = "/".join(parts)
        if value.endswith(".ts"):
            value = value[:-3]
        if not value.startswith("."):
            value = f"./{value}"
        return ModulePathFacts(
            kind=ModulePathKind.RELATIVE,
            specifier=value,
            current_artifact=request.current_artifact,
            provider_artifact=request.provider_artifact,
            relative_path=value,
        )


@dataclass(frozen=True, slots=True)
class FakeEngine:
    plugin: PluginDescriptor = _plugin("fake-engine", PluginCategory.TEMPLATE_ENGINE)
    suffixes: tuple[str, ...] = (".fake",)

    def render(
        self,
        request: RenderRequest,
        cancellation: CancellationToken,
    ) -> RenderResult:
        cancellation.raise_if_cancelled()
        roots = dict(request.context)
        schema = roots.get("schema")
        content = (
            f"schema:{schema.name.raw.original}\n"
            if schema is not None
            else f"template:{request.template_id}\n"
        )
        return RenderResult(content=content)


def test_full_orchestrator_plans_dependencies_and_renders_to_memory(tmp_path) -> None:
    (tmp_path / "contract.input").write_text("ignored", encoding="utf-8")
    pack = tmp_path / "packs" / "sdk"
    (pack / "templates" / "{schemas}").mkdir(parents=True)
    (pack / "templates" / "{index}").mkdir(parents=True)
    (pack / "DryvPack.yaml").write_text(
        """
apiVersion: dryv.dev/v1
id: example/sdk
version: 1.0.0
selections:
  index:
    exports: [schemas]
  schemas:
    select: groups.schemas.objects.each
    paths: [models]
    symbols: [(schema.name.pascal.original)]
""".strip(),
        encoding="utf-8",
    )
    (pack / "templates" / "{schemas}" / "(schema.name.kebab.original).ts.fake").write_text(
        "ignored",
        encoding="utf-8",
    )
    (pack / "templates" / "{index}" / "index.ts.fake").write_text(
        "ignored",
        encoding="utf-8",
    )
    project = tmp_path / "dryv.yaml"
    project.write_text(
        """
apiVersion: dryv.dev/v1
name: example
sources:
  contract:
    adapter: fake-source
    file: contract.input
packs:
  sdk:
    source:
      local: packs/sdk
    input: contract
    output: generated
""".strip(),
        encoding="utf-8",
    )

    result = generate(
        project,
        plugins=RuntimePlugins(
            source_adapters=(FakeSource(),),
            target_adapters=(FakeTarget(),),
            template_engines=(FakeEngine(),),
        ),
    )

    assert result.ok
    assert result.data is not None
    assert result.data.output is not None
    assert tuple(item.path for item in result.data.output.artifacts) == (
        "generated/index.ts",
        "generated/models/user.ts",
    )
    assert result.data.output.get("generated/models/user.ts").text() == "schema:User\n"

    index = next(
        item for item in result.data.plan.artifacts if item.output_path == "generated/index.ts"
    )
    exported = dict(index.exports)["schemas"].modules
    assert tuple(item.specifier for item in exported) == ("./models/user",)
    assert exported[0].symbols == ("User",)
