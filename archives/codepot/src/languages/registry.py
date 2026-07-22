"""Language adapter registry."""

from __future__ import annotations

from dataclasses import dataclass, field

from archives.codepot.src.contracts.language.interface import LanguageAdapter
from archives.codepot.src.languages.dart.adapter import dart_language_adapter
from archives.codepot.src.languages.python.adapter import python_language_adapter
from archives.codepot.src.languages.typescript.adapter import typescript_language_adapter


@dataclass
class LanguageRegistry:
    """Registry for Codepotx language adapters."""

    _adapters: dict[str, LanguageAdapter] = field(default_factory=dict)

    def register(self, adapter: LanguageAdapter) -> None:
        """Register a language adapter by its key."""

        self._adapters[adapter.key] = adapter

    def get(self, key: str) -> LanguageAdapter:
        """Get a registered language adapter."""

        try:
            return self._adapters[key]
        except KeyError as exc:
            available = ", ".join(sorted(self._adapters)) or "none"
            raise ValueError(
                f"Unknown language '{key}'. Available languages: {available}."
            ) from exc

    def keys(self) -> tuple[str, ...]:
        """Return registered language keys."""

        return tuple(sorted(self._adapters))

    def has(self, key: str) -> bool:
        """Return true when a language key is registered."""

        return key in self._adapters


def create_language_registry() -> LanguageRegistry:
    """Create language registry with built-in adapters."""

    registry = LanguageRegistry()
    registry.register(typescript_language_adapter)
    registry.register(python_language_adapter)
    registry.register(dart_language_adapter)

    return registry


language_registry = create_language_registry()
