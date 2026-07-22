"""Language adapter discovery.

Discovery imports language adapter modules from folders under src/languages.
Adapters register themselves through the decorator registry.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

from contracts.language import LanguageAdapter
from languages.decorators import get_registered_adapter, list_registered_languages

ADAPTER_MODULE_NAME = "adapter"


class LanguageDiscoveryError(LookupError):
    """Raised when a requested language cannot be discovered."""


def discover_languages() -> tuple[str, ...]:
    """Import all language adapter modules and return available languages."""
    _import_language_adapter_modules()
    return list_registered_languages()


def resolve_language_adapter(language: str) -> LanguageAdapter:
    """Resolve and instantiate a language adapter by name or alias."""
    discover_languages()

    adapter_class = get_registered_adapter(language)
    if adapter_class is None:
        available = ", ".join(discover_languages()) or "none"
        raise LanguageDiscoveryError(f"Unknown language: {language}. Available languages: {available}")

    return adapter_class()


def _import_language_adapter_modules() -> None:
    languages_root = Path(__file__).parent

    for child in sorted(languages_root.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue

        adapter_file = child / f"{ADAPTER_MODULE_NAME}.py"
        if not adapter_file.exists():
            continue

        import_module(f"languages.{child.name}.{ADAPTER_MODULE_NAME}")
