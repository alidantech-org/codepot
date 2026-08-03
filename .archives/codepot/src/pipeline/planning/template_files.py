"""Filesystem template file discovery for output planning."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from archives.codepot.src.contracts.templates.config.package import TemplatePackageConfig

CONFIG_FILE_NAMES = {
    "codepotx.yaml",
    "codepotx.yml",
    "codepotx.json",
}

IGNORE_FILE_NAME = ".codepotxIgnore"
TEMPLATE_SUFFIX = ".j2"
INDEX_STEMS = {"index", "__init__"}


class TemplateFileRole(StrEnum):
    """Role assigned to one filesystem template package file."""

    STATIC = "static"
    RENDER_ONCE = "render_once"
    CONFIGURED = "configured"
    BARREL = "barrel"


@dataclass(frozen=True)
class DiscoveredTemplateFile:
    """One discovered filesystem file inside a template package."""

    absolute_path: Path
    relative_path: Path
    relative_template_path: str
    output_relative_path: Path
    role: TemplateFileRole
    template_id: str


def _is_config_file(path: Path) -> bool:
    """Return true for template package config files."""

    return path.name in CONFIG_FILE_NAMES


def _is_builtin_ignored(path: Path) -> bool:
    """Return true when a file should never be emitted."""

    return path.name in {IGNORE_FILE_NAME, ".DS_Store"} or _is_config_file(path)


def _load_ignore_patterns(package_path: Path, config: TemplatePackageConfig) -> tuple[str, ...]:
    """Load ignore patterns from config and .codepotxIgnore."""

    patterns: list[str] = []

    ignore_patterns = config.ignore.get("patterns")
    if isinstance(ignore_patterns, list):
        patterns.extend(str(pattern) for pattern in ignore_patterns)

    ignore_file = config.ignore.get("file", IGNORE_FILE_NAME)
    ignore_path = package_path / str(ignore_file)

    if ignore_path.is_file():
        for line in ignore_path.read_text(encoding="utf-8").splitlines():
            value = line.strip()
            if value and not value.startswith("#"):
                patterns.append(value)

    return tuple(patterns)


def _matches_pattern(relative_path: Path, pattern: str) -> bool:
    """Return true when a relative path matches one simple ignore pattern."""

    path_text = relative_path.as_posix()

    if pattern.endswith("/"):
        folder = pattern.strip("/")
        return path_text == folder or path_text.startswith(f"{folder}/")

    if pattern.startswith("*."):
        return relative_path.name.endswith(pattern[1:])

    return path_text == pattern or relative_path.name == pattern


def _is_ignored(
    *,
    relative_path: Path,
    patterns: tuple[str, ...],
) -> bool:
    """Return true when a relative path is ignored by user patterns."""

    return any(_matches_pattern(relative_path, pattern) for pattern in patterns)


def _template_key_from_parts(parts: tuple[str, ...]) -> str | None:
    """Return template key when a path contains one literal {key} folder."""

    keys = tuple(
        part[1:-1]
        for part in parts
        if part.startswith("{") and part.endswith("}") and len(part) > 2
    )

    if not keys:
        return None

    if len(keys) > 1:
        raise ValueError(
            "Template file paths may contain only one configured {key} folder."
        )

    return keys[0]


def _is_template(path: Path) -> bool:
    """Return true when a file is a renderable template."""

    return path.name.endswith(TEMPLATE_SUFFIX)


def _strip_template_suffix(path: Path) -> Path:
    """Remove the template suffix from an output path."""

    if not path.name.endswith(TEMPLATE_SUFFIX):
        return path

    return path.with_name(path.name[: -len(TEMPLATE_SUFFIX)])


def _remove_config_key_segment(relative_path: Path, template_id: str) -> Path:
    """Remove the literal {key} segment from a relative path."""

    marker = f"{{{template_id}}}"
    parts = tuple(part for part in relative_path.parts if part != marker)
    return Path(*parts)


def _is_barrel_template(relative_path: Path) -> bool:
    """Return true when a configured template file is a barrel template."""

    output_path = _strip_template_suffix(relative_path)
    return output_path.stem in INDEX_STEMS


def _role_for_file(
    *,
    relative_path: Path,
    template_id: str | None,
) -> TemplateFileRole:
    """Classify one template package file."""

    if template_id is None:
        return TemplateFileRole.RENDER_ONCE if _is_template(relative_path) else TemplateFileRole.STATIC  # noqa: E501

    if _is_barrel_template(relative_path):
        return TemplateFileRole.BARREL

    return TemplateFileRole.CONFIGURED


def _output_relative_path(
    *,
    relative_path: Path,
    template_id: str | None,
) -> Path:
    """Create default output path from filesystem path."""

    if template_id is None:
        return _strip_template_suffix(relative_path)

    without_key = _remove_config_key_segment(relative_path, template_id)
    return _strip_template_suffix(without_key)


def _discovered_file(
    *,
    package_path: Path,
    path: Path,
) -> DiscoveredTemplateFile:
    """Create discovered file metadata for one package file."""

    relative_path = path.relative_to(package_path)
    template_id = _template_key_from_parts(relative_path.parts)
    role = _role_for_file(relative_path=relative_path, template_id=template_id)

    return DiscoveredTemplateFile(
        absolute_path=path,
        relative_path=relative_path,
        relative_template_path=relative_path.as_posix(),
        output_relative_path=_output_relative_path(
            relative_path=relative_path,
            template_id=template_id,
        ),
        role=role,
        template_id=template_id or "once",
    )


def discover_template_files(
    *,
    package_path: Path,
    config: TemplatePackageConfig,
) -> tuple[DiscoveredTemplateFile, ...]:
    """Discover all emit-eligible files in a template package."""

    ignore_patterns = _load_ignore_patterns(package_path, config)
    discovered: list[DiscoveredTemplateFile] = []

    for path in sorted(package_path.rglob("*")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(package_path)

        if _is_builtin_ignored(relative_path):
            continue

        if _is_ignored(relative_path=relative_path, patterns=ignore_patterns):
            continue

        file = _discovered_file(package_path=package_path, path=path)

        if file.role in {TemplateFileRole.CONFIGURED, TemplateFileRole.BARREL} and file.template_id not in config.templates:  # noqa: E501
            raise ValueError(
                f"Template file path uses unknown config key: {{{file.template_id}}}"
            )

        discovered.append(file)

    return tuple(discovered)