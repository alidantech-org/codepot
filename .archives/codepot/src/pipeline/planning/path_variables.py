"""Typed output path variable contexts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.contracts.language.runtime import LanguageRuntime
from archives.codepot.src.contracts.spec.names import SpecName
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.pipeline.planning.selections import PlannedSelection
from archives.codepot.src.spec.repository.names import create_spec_name
from archives.codepot.src.spec.utils.constants import GLOBAL_OWNER_KEY


@dataclass(frozen=True)
class PathNameVariables:
    """Name variables available during output path expansion."""

    raw: str
    clean: str
    pascal: str
    camel: str
    snake: str
    kebab: str
    screaming_snake: str
    constant: str
    path: str


@dataclass(frozen=True)
class PathOwnerVariables:
    """Owner variables available during output path expansion."""

    key: str
    name: PathNameVariables
    folders: tuple[str, ...] = ()
    is_global: bool = False


@dataclass(frozen=True)
class PathItemVariables:
    """Selected item variables available during output path expansion."""

    id: str
    key: str
    ref: str
    name: PathNameVariables


@dataclass(frozen=True)
class PathTemplateVariables:
    """Template variables available during output path expansion."""

    id: str
    select: str


@dataclass(frozen=True)
class PathLanguageVariables:
    """Language variables available during output path expansion."""

    name: str
    extensions: tuple[str, ...]
    package_name: str | None

    @property
    def extension(self) -> str:
        """Return primary extension for compatibility in path variables."""

        return self.extensions[0] if self.extensions else ""


@dataclass(frozen=True)
class PathProjectVariables:
    """Project variables available during output path expansion."""

    key: str
    version: str
    title: str


@dataclass(frozen=True)
class PathGlobalVariables:
    """Global variables available during output path expansion."""

    alias: str
    output_root: Path


@dataclass(frozen=True)
class OutputPathVariables:
    """Complete lightweight output path variables."""

    global_context: PathGlobalVariables
    project: PathProjectVariables
    language: PathLanguageVariables
    template: PathTemplateVariables

    item: PathItemVariables | None = None
    owner: PathOwnerVariables | None = None


def name_variables(name: SpecName) -> PathNameVariables:
    """Create path name variables from a spec name."""

    return PathNameVariables(
        raw=name.raw,
        clean=name.clean,
        pascal=name.pascal,
        camel=name.camel,
        snake=name.snake,
        kebab=name.kebab,
        screaming_snake=name.screaming_snake,
        constant=name.constant,
        path=name.path,
    )


def item_variables(record: SpecRecord[object]) -> PathItemVariables:
    """Create item path variables from a selected record."""

    return PathItemVariables(
        id=record.id,
        key=record.key,
        ref=record.ref.value,
        name=name_variables(record.name),
    )


def owner_variables(record: SpecRecord[object]) -> PathOwnerVariables:
    """Create owner path variables from a selected record."""

    return PathOwnerVariables(
        key=record.owner.key,
        name=name_variables(record.owner.name),
        folders=record.owner.folders,
        is_global=record.owner.is_global,
    )


def language_variables(runtime: LanguageRuntime) -> PathLanguageVariables:
    """Create language path variables."""

    return PathLanguageVariables(
        name=runtime.name,
        extensions=runtime.extensions,
        package_name=runtime.package_name,
    )


def template_variables(selection: PlannedSelection) -> PathTemplateVariables:
    """Create template path variables."""

    return PathTemplateVariables(
        id=selection.template_id,
        select=selection.select.raw,
    )


def global_owner_variables(
    *,
    alias: str,
    folders: tuple[str, ...],
) -> PathOwnerVariables:
    """Create global owner variables from template config."""

    name = create_spec_name(alias)

    return PathOwnerVariables(
        key=GLOBAL_OWNER_KEY,
        name=name_variables(name),
        folders=folders,
        is_global=True,
    )


def owner_variables_from_key_with_folders(
    owner_key: str,
    folders: tuple[str, ...],
) -> PathOwnerVariables:
    """Create owner path variables from a selection bucket key with folders."""

    name = create_spec_name(owner_key)

    return PathOwnerVariables(
        key=owner_key,
        name=name_variables(name),
        folders=folders,
        is_global=owner_key == GLOBAL_OWNER_KEY,
    )