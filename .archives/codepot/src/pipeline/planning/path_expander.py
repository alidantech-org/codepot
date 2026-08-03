"""Safe output path variable expansion."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.pipeline.planning.path_debug import PathVariableRead
from archives.codepot.src.pipeline.planning.path_variables import OutputPathVariables

ESCAPED_OPEN_BRACKET = "\0CODEPOTX_OPEN_BRACKET\0"
ESCAPED_CLOSE_BRACKET = "\0CODEPOTX_CLOSE_BRACKET\0"

VARIABLE_PATTERN = re.compile(
    r"(?<!\[)\[([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\](?!\])"
)


@dataclass(frozen=True)
class ExpandedPathPart:
    """One expanded output path part."""

    value: str


@dataclass(frozen=True)
class PathExpansionResult:
    """Expanded path parts plus variable debug reads."""

    parts: tuple[ExpandedPathPart, ...]
    reads: tuple[PathVariableRead, ...]


def _split_variable_path(path: str) -> tuple[str, ...]:
    """Split a variable path into access tokens."""

    return tuple(part for part in path.split(".") if part)


def _read_name_token(
    *,
    raw_variable: str,
    token: str,
    raw: str,
    clean: str,
    pascal: str,
    camel: str,
    snake: str,
    kebab: str,
    screaming_snake: str,
    constant: str,
    path: str,
) -> str:
    """Resolve a typed name token."""

    if token == "raw":
        return raw
    if token == "clean":
        return clean
    if token == "pascal":
        return pascal
    if token == "camel":
        return camel
    if token == "snake":
        return snake
    if token == "kebab":
        return kebab
    if token == "screaming_snake":
        return screaming_snake
    if token == "constant":
        return constant
    if token == "path":
        return path

    raise ValueError(f"Unsupported name token '{token}' in [{raw_variable}]")


def _read_name(root, raw_variable: str, token: str) -> str:
    """Read a supported name token from a name variable object."""

    return _read_name_token(
        raw_variable=raw_variable,
        token=token,
        raw=root.raw,
        clean=root.clean,
        pascal=root.pascal,
        camel=root.camel,
        snake=root.snake,
        kebab=root.kebab,
        screaming_snake=root.screaming_snake,
        constant=root.constant,
        path=root.path,
    )


def _read_language(variables: OutputPathVariables, raw_variable: str, token: str) -> str:
    """Read language variable."""

    if token == "name":
        return variables.language.name
    if token == "extension":
        return variables.language.extension
    if token == "package_name" and variables.language.package_name is not None:
        return variables.language.package_name

    raise ValueError(f"Unsupported language variable: [{raw_variable}]")


def _read_template(variables: OutputPathVariables, raw_variable: str, token: str) -> str:
    """Read template variable."""

    if token == "id":
        return variables.template.id
    if token == "select":
        return variables.template.select

    raise ValueError(f"Unsupported template variable: [{raw_variable}]")


def _read_project(variables: OutputPathVariables, raw_variable: str, token: str) -> str:
    """Read project variable."""

    if token == "key":
        return variables.project.key
    if token == "version":
        return variables.project.version
    if token == "title":
        return variables.project.title

    raise ValueError(f"Unsupported project variable: [{raw_variable}]")


def _read_global(variables: OutputPathVariables, raw_variable: str, token: str) -> str:
    """Read global variable."""

    if token == "alias":
        return variables.global_context.alias

    raise ValueError(f"Unsupported global variable: [{raw_variable}]")


def _read_item(
    variables: OutputPathVariables,
    raw_variable: str,
    parts: tuple[str, ...],
) -> str:
    """Read item variable."""

    if variables.item is None:
        raise ValueError(f"Variable requires selected item context: [{raw_variable}]")

    if len(parts) == 2:
        if parts[1] == "id":
            return variables.item.id
        if parts[1] == "key":
            return variables.item.key
        if parts[1] == "ref":
            return variables.item.ref

    if len(parts) == 3 and parts[1] == "name":
        return _read_name(variables.item.name, raw_variable, parts[2])

    raise ValueError(f"Unsupported item variable: [{raw_variable}]")


def _read_owner(
    variables: OutputPathVariables,
    raw_variable: str,
    parts: tuple[str, ...],
) -> str:
    """Read owner variable."""

    if variables.owner is None:
        raise ValueError(f"Variable requires owner context: [{raw_variable}]")

    if len(parts) == 2:
        if parts[1] == "key":
            return variables.owner.key
        if parts[1] == "folders":
            return "/".join(variables.owner.folders)

    if len(parts) == 3 and parts[1] == "name":
        return _read_name(variables.owner.name, raw_variable, parts[2])

    raise ValueError(f"Unsupported owner variable: [{raw_variable}]")


def _read_variable(variables: OutputPathVariables, raw_variable: str) -> str:
    """Resolve one output path variable."""

    parts = _split_variable_path(raw_variable)

    if len(parts) < 2:
        raise ValueError(f"Invalid output path variable: [{raw_variable}]")

    root = parts[0]

    if root == "language" and len(parts) == 2:
        return _read_language(variables, raw_variable, parts[1])
    if root == "template" and len(parts) == 2:
        return _read_template(variables, raw_variable, parts[1])
    if root == "project" and len(parts) == 2:
        return _read_project(variables, raw_variable, parts[1])
    if root == "global" and len(parts) == 2:
        return _read_global(variables, raw_variable, parts[1])
    if root == "item":
        return _read_item(variables, raw_variable, parts)
    if root == "owner":
        return _read_owner(variables, raw_variable, parts)

    raise ValueError(f"Unsupported output path variable: [{raw_variable}]")


def _escape_literal_brackets(text: str) -> str:
    """Protect escaped literal brackets before variable expansion."""

    return (
        text.replace("[[", ESCAPED_OPEN_BRACKET)
        .replace("]]", ESCAPED_CLOSE_BRACKET)
    )


def _restore_literal_brackets(text: str) -> str:
    """Restore escaped literal brackets after variable expansion."""

    return (
        text.replace(ESCAPED_OPEN_BRACKET, "[")
        .replace(ESCAPED_CLOSE_BRACKET, "]")
    )


def expand_path_text(
    text: str,
    variables: OutputPathVariables,
    reads: list[PathVariableRead],
) -> str:
    """Expand all output path variables in one text segment."""

    escaped = _escape_literal_brackets(text)

    def replace(match: re.Match[str]) -> str:
        variable = match.group(1)
        value = _read_variable(variables, variable)
        reads.append(PathVariableRead(variable=variable, value=value))
        return value

    return _restore_literal_brackets(VARIABLE_PATTERN.sub(replace, escaped))


def safe_path_part(value: str) -> str:
    """Normalize and validate one output path segment."""

    normalized = value.strip().replace("\\", "/").strip("/")

    if not normalized:
        return ""

    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Unsafe output path segment: {value}")

    return normalized


def expand_path_parts(
    parts: tuple[str, ...],
    variables: OutputPathVariables,
) -> PathExpansionResult:
    """Expand path parts into safe output path parts."""

    expanded: list[ExpandedPathPart] = []
    reads: list[PathVariableRead] = []

    for part in parts:
        value = safe_path_part(expand_path_text(part, variables, reads))
        if value:
            expanded.append(ExpandedPathPart(value=value))

    return PathExpansionResult(
        parts=tuple(expanded),
        reads=tuple(reads),
    )


def join_expanded_path(
    *,
    output_root: Path,
    folders: tuple[ExpandedPathPart, ...],
    file: ExpandedPathPart,
) -> Path:
    """Join expanded folders and file under output root."""

    folder_values = tuple(folder.value for folder in folders)

    if folder_values:
        return output_root.joinpath(*folder_values, file.value)

    return output_root / file.value