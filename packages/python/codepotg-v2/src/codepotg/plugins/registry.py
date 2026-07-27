from __future__ import annotations

from dataclasses import dataclass

from codepotg.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity

from .descriptors import PluginCategory, PluginDescriptor


@dataclass(frozen=True, slots=True)
class PluginRegistry:
    descriptors: tuple[PluginDescriptor, ...]
    diagnostics: Diagnostics = Diagnostics()

    @classmethod
    def build(cls, descriptors: tuple[PluginDescriptor, ...]) -> PluginRegistry:
        ordered = tuple(sorted(descriptors, key=lambda item: (item.category.value, item.id)))
        diagnostics: list[Diagnostic] = []
        owners: dict[tuple[PluginCategory, str], PluginDescriptor] = {}

        for descriptor in ordered:
            for identifier in (descriptor.id, *descriptor.aliases):
                key = (descriptor.category, identifier)
                previous = owners.get(key)
                if previous is None:
                    owners[key] = descriptor
                    continue
                diagnostics.append(
                    Diagnostic(
                        code="PLUGIN_IDENTIFIER_CONFLICT",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            f"plugin identifier {identifier!r} is claimed by both "
                            f"{previous.id!r} and {descriptor.id!r}"
                        ),
                        details=(
                            ("category", descriptor.category.value),
                            ("identifier", identifier),
                        ),
                    )
                )

        return cls(ordered, Diagnostics.from_iterable(diagnostics))

    def resolve(self, category: PluginCategory, identifier: str) -> PluginDescriptor | None:
        matches = tuple(
            descriptor
            for descriptor in self.descriptors
            if descriptor.category is category
            and (descriptor.id == identifier or identifier in descriptor.aliases)
        )
        return matches[0] if len(matches) == 1 else None

    def require_capabilities(
        self,
        category: PluginCategory,
        identifier: str,
        capabilities: tuple[str, ...],
    ) -> Diagnostics:
        descriptor = self.resolve(category, identifier)
        if descriptor is None:
            return Diagnostics(
                (
                    Diagnostic(
                        code="PLUGIN_NOT_FOUND",
                        severity=DiagnosticSeverity.ERROR,
                        message=f"plugin {category.value}:{identifier} is not available",
                        details=(("category", category.value), ("identifier", identifier)),
                    ),
                )
            )
        missing = tuple(sorted(set(capabilities) - set(descriptor.capabilities)))
        if not missing:
            return Diagnostics()
        return Diagnostics(
            (
                Diagnostic(
                    code="PLUGIN_CAPABILITY_MISSING",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"plugin {descriptor.id!r} is missing required capabilities",
                    details=(("capabilities", missing), ("plugin", descriptor.id)),
                ),
            )
        )
