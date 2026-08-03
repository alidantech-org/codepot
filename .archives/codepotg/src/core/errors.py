from __future__ import annotations


class GeneratorError(Exception):
    """Base error for all generator failures."""


class PathResolutionError(GeneratorError):
    """Raised when project paths cannot be resolved."""


class ConfigError(GeneratorError):
    """Raised when config loading or validation fails."""


class OpenApiLoadError(GeneratorError):
    """Raised when the OpenAPI document cannot be loaded."""


class CommandError(GeneratorError):
    """Raised when a CLI command cannot complete."""
