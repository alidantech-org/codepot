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
from .options import DartTargetOptions
from .targets import DART_CAPABILITIES, TARGETS
from .validation import validate_identifier, validate_output_path


@dataclass(frozen=True, slots=True)
class DartTargetAdapter:
    options: DartTargetOptions = field(default_factory=DartTargetOptions)
    _plugin: PluginDescriptor = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "_plugin",
            PluginDescriptor(
                id="dart",
                category=PluginCategory.TARGET_ADAPTER,
                distribution="codepotg-language-dart",
                version=Version.parse("0.1.0-alpha.1"),
                api_version=PLUGIN_API_VERSION,
                ir_version=IR_API_VERSION,
                aliases=(),
                capabilities=DART_CAPABILITIES,
                trust=PluginTrust.EXECUTABLE,
                documentation="Dart validation and URI facts; no source rendering.",
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
