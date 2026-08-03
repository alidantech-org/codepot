"""Template package validator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.contracts.templates.config.package import LoadedTemplatePackageConfig
from archives.codepot.src.pipeline.templates.refs import validate_template_ref
from archives.codepot.src.pipeline.templates.selection import validate_template_select


@dataclass(frozen=True)
class TemplateValidationError:
    """One template validation error."""

    template_id: str | None
    message: str


@dataclass(frozen=True)
class TemplateValidationWarning:
    """One template validation warning."""

    template_id: str | None
    message: str


@dataclass(frozen=True)
class TemplateValidationResult:
    """Template package validation result."""

    errors: tuple[TemplateValidationError, ...]
    warnings: tuple[TemplateValidationWarning, ...]

    @property
    def is_valid(self) -> bool:
        """Return true when no validation errors exist."""

        return not self.errors


def _template_key_marker(template_id: str) -> str:
    """Return the literal folder marker for a configured template key."""

    return f"{{{template_id}}}"


def _has_template_key_folder(
    *,
    package_path: Path,
    template_id: str,
) -> bool:
    """Return true when the package has a folder named {template_id}."""

    marker = _template_key_marker(template_id)

    return any(path.is_dir() and path.name == marker for path in package_path.rglob("*"))


def validate_template_package(
    package: LoadedTemplatePackageConfig,
) -> TemplateValidationResult:
    """Validate loaded template package config."""

    errors: list[TemplateValidationError] = []
    warnings: list[TemplateValidationWarning] = []

    config = package.config

    for template_id, template in config.templates.items():
        try:
            validate_template_select(template.select)
        except ValueError as error:
            errors.append(
                TemplateValidationError(
                    template_id=template_id,
                    message=str(error),
                )
            )

        if not _has_template_key_folder(
            package_path=package.package_path,
            template_id=template_id,
        ):
            errors.append(
                TemplateValidationError(
                    template_id=template_id,
                    message=(
                        f"Configured template key '{template_id}' requires a "
                        f"filesystem folder named {_template_key_marker(template_id)}."
                    ),
                )
            )

        for subject, resolver in template.resolves.items():
            try:
                validate_template_ref(value=resolver.ref, config=config)
            except ValueError as error:
                errors.append(
                    TemplateValidationError(
                        template_id=template_id,
                        message=f"Invalid resolver for {subject}: {error}",
                    )
                )

    if not config.templates:
        warnings.append(
            TemplateValidationWarning(
                template_id=None,
                message=(
                    "Template package contains no configured dynamic templates. "
                    "Only normal filesystem files will be emitted."
                ),
            )
        )

    return TemplateValidationResult(
        errors=tuple(errors),
        warnings=tuple(warnings),
    )