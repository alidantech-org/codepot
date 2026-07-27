from __future__ import annotations

from dataclasses import dataclass, field

from codepotg.diagnostics import Diagnostics
from codepotg.plugins import PluginCategory, PluginDescriptor, PluginTrust
from codepotg.ports import (
    IdentifierValidationRequest,
    ModulePathFacts,
    ModulePathRequest,
    OutputPathValidationRequest,
    TargetDescriptor,
)
from codepotg.versions import IR_API_VERSION, PLUGIN_API_VERSION, Version

from .modules import resolve_module_path
from .options import TypeScriptTargetOptions
from .targets import TARGETS, TYPESCRIPT_CAPABILITIES
from .validation import validate_identifier, validate_output_path


@dataclass(frozen=True, slots=True)
class TypeScriptTargetAdapter:
    options: TypeScriptTargetOptions = field(default_factory=TypeScriptTargetOptions)
    _plugin: PluginDescriptor = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.options, TypeScriptTargetOptions):
            raise ValueError("options must be a TypeScriptTargetOptions instance")
        object.__setattr__(
            self,
            "_plugin",
            PluginDescriptor(
                id="typescript",
                category=PluginCategory.TARGET_ADAPTER,
                distribution="codepotg-language-typescript",
                version=Version.parse("0.1.0-alpha.1"),
                api_version=PLUGIN_API_VERSION,
                ir_version=IR_API_VERSION,
                aliases=(),
                capabilities=TYPESCRIPT_CAPABILITIES,
                trust=PluginTrust.EXECUTABLE,
                documentation=(
                    "TypeScript validation and module-path facts; no source rendering."
                ),
            ),
        )

    @property
    def plugin(self) -> PluginDescriptor:
        return self._plugin

    @property
    def targets(self) -> tuple[TargetDescriptor, ...]:
        return TARGETS

    def validate_identifier(
        self,
        request: IdentifierValidationRequest,
    ) -> Diagnostics:
        return validate_identifier(request, self.options)

    def validate_output_path(
        self,
        request: OutputPathValidationRequest,
    ) -> Diagnostics:
        return validate_output_path(request)

    def resolve_module_path(self, request: ModulePathRequest) -> ModulePathFacts:
        return resolve_module_path(request, self.options)
