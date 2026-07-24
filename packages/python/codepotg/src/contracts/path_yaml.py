"""paths.yaml contract loading helpers."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from contracts.paths import (
    PathBarrel,
    PathConfig,
    PathDependencyProvider,
    PathEmission,
    PathFolder,
    PathImportConfig,
    PathLifecycleMode,
    PathSelection,
    PathSelectionMode,
    PathSelectionScope,
    PathWritePolicy,
    default_path_rules,
)

KEY_FOLDERS = "folders"
KEY_SELECTIONS = "selections"
KEY_EMISSIONS = "emissions"
KEY_BARRELS = "barrels"
KEY_IMPORTS = "imports"
KEY_STRATEGY = "strategy"
KEY_SELECT = "select"
KEY_SELECTION = "selection"
KEY_AS = "as"
KEY_ALIAS = "alias"
KEY_MODE = "mode"
KEY_SCOPE = "scope"
KEY_PARTS = "parts"
KEY_OUTPUT = "output"
KEY_TEMPLATE = "template"
KEY_PROVIDES = "provides"
KEY_EXPORTS = "exports"
KEY_LIFECYCLE = "lifecycle"
KEY_DESCRIPTION = "description"
KEY_TEMPLATE_EXTENSION = "template_extension"
KEY_STRIP_TEMPLATE_EXTENSION = "strip_template_extension"
KEY_ALLOW_RAW_FILES = "allow_raw_files"
KEY_META = "meta"
KEY_WRITE_POLICY = "write_policy"
KEY_DEFAULT_MODE = "default_mode"
KEY_MANAGED_ROOTS = "managed_roots"
KEY_IMMUTABLE_ROOTS = "immutable_roots"
KEY_PROTECTED_ROOTS = "protected_roots"
KEY_CLEAN_ROOTS = "clean_roots"

DEFAULT_TEMPLATE_EXTENSION = ".j2"
IMPORT_STRATEGY_RELATIVE = "relative"
IMPORT_STRATEGY_PACKAGE = "package"
IMPORT_STRATEGY_NONE = "none"

ALLOWED_IMPORT_STRATEGIES = {
    IMPORT_STRATEGY_RELATIVE,
    IMPORT_STRATEGY_PACKAGE,
    IMPORT_STRATEGY_NONE,
}
_ALLOWED_ROOT_KEYS = {
    KEY_FOLDERS,
    KEY_SELECTIONS,
    KEY_EMISSIONS,
    KEY_BARRELS,
    KEY_IMPORTS,
    KEY_TEMPLATE_EXTENSION,
    KEY_STRIP_TEMPLATE_EXTENSION,
    KEY_ALLOW_RAW_FILES,
    KEY_META,
    KEY_WRITE_POLICY,
}
_ALLOWED_FOLDER_KEYS = {
    KEY_SELECT,
    KEY_AS,
    KEY_ALIAS,
    KEY_MODE,
    KEY_PARTS,
    KEY_DESCRIPTION,
}
_ALLOWED_SELECTION_KEYS = {
    KEY_SELECT,
    KEY_AS,
    KEY_ALIAS,
    KEY_SCOPE,
    KEY_DESCRIPTION,
}
_ALLOWED_EMISSION_KEYS = {
    KEY_SELECTION,
    KEY_TEMPLATE,
    KEY_OUTPUT,
    KEY_IMPORTS,
    KEY_PROVIDES,
    KEY_LIFECYCLE,
    KEY_DESCRIPTION,
}
_ALLOWED_BARREL_KEYS = {
    KEY_TEMPLATE,
    KEY_OUTPUT,
    KEY_EXPORTS,
    KEY_SCOPE,
    KEY_AS,
    KEY_ALIAS,
    KEY_LIFECYCLE,
    KEY_DESCRIPTION,
}
_ALLOWED_IMPORT_KEYS = {KEY_STRATEGY}
_ALLOWED_WRITE_POLICY_KEYS = {
    KEY_DEFAULT_MODE,
    KEY_MANAGED_ROOTS,
    KEY_IMMUTABLE_ROOTS,
    KEY_PROTECTED_ROOTS,
    KEY_CLEAN_ROOTS,
}


class PathYamlError(ValueError):
    """Raised when paths.yaml contains invalid structure."""


def path_config_from_yaml(
    data: dict[str, Any] | None,
    *,
    strict: bool = False,
) -> PathConfig:
    """Build a validated PathConfig from parsed paths.yaml data.

    Existing folder-only packs remain valid. The named selection/emission graph is
    additive, but its references are always validated because unresolved graph
    nodes cannot be generated safely.
    """

    if data is None:
        data = {}

    if not isinstance(data, dict):
        raise PathYamlError("paths.yaml root must be an object.")

    if strict:
        _reject_unknown_keys(data, _ALLOWED_ROOT_KEYS, owner="paths.yaml")

    selections = _parse_selections(data.get(KEY_SELECTIONS), strict=strict)
    emissions = _parse_emissions(data.get(KEY_EMISSIONS), strict=strict)
    barrels = _parse_barrels(data.get(KEY_BARRELS), strict=strict)
    _validate_graph(selections=selections, emissions=emissions, barrels=barrels)

    return PathConfig(
        folders=_parse_folders(data.get(KEY_FOLDERS, {}), strict=strict),
        selections=selections,
        emissions=emissions,
        barrels=barrels,
        imports=_parse_imports(data.get(KEY_IMPORTS), strict=strict),
        template_extension=_string(
            data.get(KEY_TEMPLATE_EXTENSION),
            default=DEFAULT_TEMPLATE_EXTENSION,
            field_name=KEY_TEMPLATE_EXTENSION,
        ),
        strip_template_extension=_bool(
            data.get(KEY_STRIP_TEMPLATE_EXTENSION),
            default=True,
            field_name=KEY_STRIP_TEMPLATE_EXTENSION,
        ),
        allow_raw_files=_bool(
            data.get(KEY_ALLOW_RAW_FILES),
            default=True,
            field_name=KEY_ALLOW_RAW_FILES,
        ),
        write_policy=_parse_write_policy(data.get(KEY_WRITE_POLICY), strict=strict),
        rules=default_path_rules(),
        meta=_dict(data.get(KEY_META), field_name=KEY_META),
    )


def _parse_write_policy(raw: Any, *, strict: bool) -> PathWritePolicy:
    if raw is None:
        return PathWritePolicy()
    if not isinstance(raw, dict):
        raise PathYamlError("'write_policy' must be an object.")
    if strict:
        _reject_unknown_keys(raw, _ALLOWED_WRITE_POLICY_KEYS, owner=KEY_WRITE_POLICY)
    return PathWritePolicy(
        exists=True,
        default_mode=_required_lifecycle(
            raw.get(KEY_DEFAULT_MODE),
            default=PathLifecycleMode.MANAGED,
            field_name=KEY_DEFAULT_MODE,
        ),
        managed_roots=_string_list(raw.get(KEY_MANAGED_ROOTS), field_name=KEY_MANAGED_ROOTS),
        immutable_roots=_string_list(raw.get(KEY_IMMUTABLE_ROOTS), field_name=KEY_IMMUTABLE_ROOTS),
        protected_roots=_string_list(raw.get(KEY_PROTECTED_ROOTS), field_name=KEY_PROTECTED_ROOTS),
        clean_roots=_string_list(raw.get(KEY_CLEAN_ROOTS), field_name=KEY_CLEAN_ROOTS),
    )


def _parse_imports(raw: Any, *, strict: bool) -> PathImportConfig:
    if raw is None:
        return PathImportConfig()

    if not isinstance(raw, dict):
        raise PathYamlError("'imports' must be an object.")
    if strict:
        _reject_unknown_keys(raw, _ALLOWED_IMPORT_KEYS, owner=KEY_IMPORTS)

    strategy = _string(
        raw.get(KEY_STRATEGY),
        default=IMPORT_STRATEGY_RELATIVE,
        field_name=f"{KEY_IMPORTS}.{KEY_STRATEGY}",
    )
    if strategy not in ALLOWED_IMPORT_STRATEGIES:
        allowed = ", ".join(sorted(ALLOWED_IMPORT_STRATEGIES))
        raise PathYamlError(f"Invalid imports.strategy: {strategy}. Allowed: {allowed}.")

    return PathImportConfig(strategy=strategy)


def _parse_folders(raw: Any, *, strict: bool) -> tuple[PathFolder, ...]:
    if raw is None:
        return ()
    mapping = _named_mapping(raw, field_name=KEY_FOLDERS)
    folders: list[PathFolder] = []
    for name, value in mapping.items():
        if strict:
            _reject_unknown_keys(value, _ALLOWED_FOLDER_KEYS, owner=f"folders.{name}")
        folders.append(_parse_folder(name, value))
    return tuple(folders)


def _parse_folder(name: str, raw: dict[str, Any]) -> PathFolder:
    mode_value = raw.get(KEY_MODE)
    lifecycle = _legacy_lifecycle_mode(mode_value)
    mode = (
        PathSelectionMode.ONCE
        if str(mode_value) == "once" or (lifecycle is not None and raw.get(KEY_SELECT) is None)
        else _mode(None, folder=name)
    )
    if lifecycle is None:
        mode = _mode(mode_value, folder=name)
    select = _optional_select(raw, name=name, mode=mode)
    alias = _alias(raw, name=name, default=name)

    return PathFolder(
        name=name,
        select=select,
        alias=alias,
        parts=_parse_parts(raw.get(KEY_PARTS), owner=f"{KEY_FOLDERS}.{name}.{KEY_PARTS}"),
        mode=mode,
        lifecycle=lifecycle,
        description=_string(
            raw.get(KEY_DESCRIPTION),
            default="-",
            field_name=f"{name}.{KEY_DESCRIPTION}",
        ),
    )


def _parse_selections(raw: Any, *, strict: bool) -> tuple[PathSelection, ...]:
    if raw is None:
        return ()
    mapping = _named_mapping(raw, field_name=KEY_SELECTIONS)
    selections: list[PathSelection] = []
    aliases: dict[str, str] = {}
    for name, value in mapping.items():
        owner = f"{KEY_SELECTIONS}.{name}"
        if strict:
            _reject_unknown_keys(value, _ALLOWED_SELECTION_KEYS, owner=owner)
        alias = _alias(value, name=name, default=name)
        existing = aliases.get(alias)
        if existing is not None:
            raise PathYamlError(
                f"Selections '{existing}' and '{name}' use the same alias '{alias}'."
            )
        aliases[alias] = name
        selections.append(
            PathSelection(
                name=name,
                select=_non_empty_string(
                    value.get(KEY_SELECT),
                    default="",
                    field_name=f"{owner}.{KEY_SELECT}",
                ),
                alias=alias,
                scope=_scope(
                    value.get(KEY_SCOPE),
                    default=PathSelectionScope.EACH,
                    field_name=f"{owner}.{KEY_SCOPE}",
                ),
                description=_string(
                    value.get(KEY_DESCRIPTION),
                    default="-",
                    field_name=f"{owner}.{KEY_DESCRIPTION}",
                ),
            )
        )
    return tuple(selections)


def _parse_emissions(raw: Any, *, strict: bool) -> tuple[PathEmission, ...]:
    if raw is None:
        return ()
    mapping = _named_mapping(raw, field_name=KEY_EMISSIONS)
    emissions: list[PathEmission] = []
    for name, value in mapping.items():
        owner = f"{KEY_EMISSIONS}.{name}"
        if strict:
            _reject_unknown_keys(value, _ALLOWED_EMISSION_KEYS, owner=owner)
        selection = _non_empty_string(
            value.get(KEY_SELECTION),
            default="",
            field_name=f"{owner}.{KEY_SELECTION}",
        )
        provides = _string_list(value.get(KEY_PROVIDES), field_name=f"{owner}.{KEY_PROVIDES}")
        emissions.append(
            PathEmission(
                name=name,
                selection=selection,
                template=_template_path(value.get(KEY_TEMPLATE), owner=owner),
                output=_parse_parts(value.get(KEY_OUTPUT), owner=f"{owner}.{KEY_OUTPUT}"),
                providers=_parse_providers(value.get(KEY_IMPORTS), owner=owner),
                provides=provides or (selection,),
                lifecycle=_optional_lifecycle(
                    value.get(KEY_LIFECYCLE),
                    field_name=f"{owner}.{KEY_LIFECYCLE}",
                ),
                description=_string(
                    value.get(KEY_DESCRIPTION),
                    default="-",
                    field_name=f"{owner}.{KEY_DESCRIPTION}",
                ),
            )
        )
    return tuple(emissions)


def _parse_barrels(raw: Any, *, strict: bool) -> tuple[PathBarrel, ...]:
    if raw is None:
        return ()
    mapping = _named_mapping(raw, field_name=KEY_BARRELS)
    barrels: list[PathBarrel] = []
    for name, value in mapping.items():
        owner = f"{KEY_BARRELS}.{name}"
        if strict:
            _reject_unknown_keys(value, _ALLOWED_BARREL_KEYS, owner=owner)
        scope = _scope(
            value.get(KEY_SCOPE),
            default=PathSelectionScope.ALL,
            field_name=f"{owner}.{KEY_SCOPE}",
        )
        if scope == PathSelectionScope.EACH:
            raise PathYamlError(
                f"'{owner}.{KEY_SCOPE}' must be 'all' or 'resource' for a barrel."
            )
        exports = _string_list(
            value.get(KEY_EXPORTS),
            field_name=f"{owner}.{KEY_EXPORTS}",
        )
        if not exports:
            raise PathYamlError(f"'{owner}.{KEY_EXPORTS}' must contain at least one output node.")
        barrels.append(
            PathBarrel(
                name=name,
                template=_template_path(value.get(KEY_TEMPLATE), owner=owner),
                output=_parse_parts(value.get(KEY_OUTPUT), owner=f"{owner}.{KEY_OUTPUT}"),
                exports=exports,
                scope=scope,
                alias=_alias(value, name=name, default="barrel"),
                lifecycle=_optional_lifecycle(
                    value.get(KEY_LIFECYCLE),
                    field_name=f"{owner}.{KEY_LIFECYCLE}",
                ),
                description=_string(
                    value.get(KEY_DESCRIPTION),
                    default="-",
                    field_name=f"{owner}.{KEY_DESCRIPTION}",
                ),
            )
        )
    return tuple(barrels)


def _parse_providers(raw: Any, *, owner: str) -> tuple[PathDependencyProvider, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, dict):
        raise PathYamlError(f"'{owner}.{KEY_IMPORTS}' must be an object of purpose: provider.")
    providers: list[PathDependencyProvider] = []
    for purpose, source in raw.items():
        purpose_name = _non_empty_string(
            purpose,
            default="",
            field_name=f"{owner}.{KEY_IMPORTS} purpose",
        )
        providers.append(
            PathDependencyProvider(
                purpose=purpose_name,
                source=_non_empty_string(
                    source,
                    default="",
                    field_name=f"{owner}.{KEY_IMPORTS}.{purpose_name}",
                ),
            )
        )
    return tuple(providers)


def _validate_graph(
    *,
    selections: tuple[PathSelection, ...],
    emissions: tuple[PathEmission, ...],
    barrels: tuple[PathBarrel, ...],
) -> None:
    selection_names = {selection.name for selection in selections}
    emission_names = {emission.name for emission in emissions}
    barrel_names = {barrel.name for barrel in barrels}
    duplicates = emission_names & barrel_names
    if duplicates:
        raise PathYamlError(
            "Output node ids must be unique across emissions and barrels: "
            + ", ".join(sorted(duplicates))
        )

    node_names = emission_names | barrel_names
    dependencies: dict[str, tuple[str, ...]] = {}

    for emission in emissions:
        if emission.selection not in selection_names:
            raise PathYamlError(
                f"Emission '{emission.name}' references unknown selection "
                f"'{emission.selection}'."
            )
        sources = tuple(provider.source for provider in emission.providers)
        for provider in emission.providers:
            if provider.source not in node_names:
                raise PathYamlError(
                    f"Emission '{emission.name}' imports '{provider.purpose}' from unknown "
                    f"provider '{provider.source}'."
                )
            if provider.source == emission.name:
                raise PathYamlError(
                    f"Emission '{emission.name}' cannot provide its own '{provider.purpose}' import."
                )
        dependencies[emission.name] = sources

    for barrel in barrels:
        for exported in barrel.exports:
            if exported not in node_names:
                raise PathYamlError(
                    f"Barrel '{barrel.name}' exports unknown output node '{exported}'."
                )
            if exported == barrel.name:
                raise PathYamlError(f"Barrel '{barrel.name}' cannot export itself.")
        dependencies[barrel.name] = barrel.exports

    _reject_dependency_cycles(dependencies)


def _reject_dependency_cycles(dependencies: dict[str, tuple[str, ...]]) -> None:
    complete: set[str] = set()
    active: list[str] = []
    active_set: set[str] = set()

    def visit(node: str) -> None:
        if node in complete:
            return
        if node in active_set:
            start = active.index(node)
            cycle = (*active[start:], node)
            raise PathYamlError("Output dependency cycle: " + " -> ".join(cycle))
        active.append(node)
        active_set.add(node)
        for dependency in dependencies.get(node, ()):
            visit(dependency)
        active.pop()
        active_set.remove(node)
        complete.add(node)

    for node in sorted(dependencies):
        visit(node)


def _named_mapping(raw: Any, *, field_name: str) -> dict[str, dict[str, Any]]:
    if not isinstance(raw, dict):
        raise PathYamlError(f"'{field_name}' must be an object.")
    result: dict[str, dict[str, Any]] = {}
    for name, value in raw.items():
        if not isinstance(name, str) or not name.strip():
            raise PathYamlError(f"'{field_name}' names must be non-empty strings.")
        if not isinstance(value, dict):
            raise PathYamlError(f"'{field_name}.{name}' must be an object.")
        result[name.strip()] = value
    return result


def _alias(raw: dict[str, Any], *, name: str, default: str) -> str:
    as_value = raw.get(KEY_AS)
    alias_value = raw.get(KEY_ALIAS)
    if as_value is not None and alias_value is not None and as_value != alias_value:
        raise PathYamlError(
            f"'{name}' defines conflicting '{KEY_AS}' and '{KEY_ALIAS}' values."
        )
    value = as_value if as_value is not None else alias_value
    return _non_empty_string(value, default=default, field_name=f"{name}.{KEY_AS}")


def _parse_parts(raw: Any, *, owner: str) -> tuple[Any, ...]:
    if not isinstance(raw, list | tuple) or not raw:
        raise PathYamlError(f"'{owner}' is required and must be a non-empty list.")
    return tuple(_parse_part(part, owner=owner) for part in raw)


def _parse_part(value: Any, *, owner: str) -> Any:
    if isinstance(value, str):
        if not value:
            raise PathYamlError(f"'{owner}' entries must be non-empty.")
        return value
    if (
        isinstance(value, list | tuple)
        and len(value) == 1
        and isinstance(value[0], str)
        and value[0]
    ):
        return f"[{value[0]}]"
    raise PathYamlError(f"'{owner}' entries must be strings or single-expression lists.")


def _template_path(value: Any, *, owner: str) -> str:
    result = _non_empty_string(
        value,
        default="",
        field_name=f"{owner}.{KEY_TEMPLATE}",
    ).replace("\\", "/")
    path = PurePosixPath(result)
    if path.is_absolute() or ".." in path.parts:
        raise PathYamlError(f"'{owner}.{KEY_TEMPLATE}' must be a safe relative POSIX path.")
    if path.name in {"paths.yaml", "paths.yml"}:
        raise PathYamlError(f"'{owner}.{KEY_TEMPLATE}' cannot reference the path config file.")
    return path.as_posix()


def _mode(value: Any, *, folder: str) -> PathSelectionMode:
    if value is None:
        return PathSelectionMode.EACH
    try:
        return PathSelectionMode(str(value))
    except ValueError as exc:
        allowed = ", ".join(item.value for item in PathSelectionMode)
        raise PathYamlError(
            f"Invalid mode for folder '{folder}': {value}. Allowed: {allowed}."
        ) from exc


def _scope(value: Any, *, default: PathSelectionScope, field_name: str) -> PathSelectionScope:
    if value is None:
        return default
    try:
        return PathSelectionScope(str(value))
    except ValueError as exc:
        allowed = ", ".join(item.value for item in PathSelectionScope)
        raise PathYamlError(f"Invalid '{field_name}': {value}. Allowed: {allowed}.") from exc


def _legacy_lifecycle_mode(value: Any) -> PathLifecycleMode | None:
    if value is None:
        return None
    value = str(value)
    if value == "once":
        return PathLifecycleMode.IMMUTABLE
    if value in {PathLifecycleMode.MANAGED.value, PathLifecycleMode.IMMUTABLE.value}:
        return PathLifecycleMode(value)
    return None


def _optional_lifecycle(value: Any, *, field_name: str) -> PathLifecycleMode | None:
    if value is None:
        return None
    try:
        return PathLifecycleMode(str(value))
    except ValueError as exc:
        allowed = ", ".join(item.value for item in PathLifecycleMode)
        raise PathYamlError(f"Invalid '{field_name}': {value}. Allowed: {allowed}.") from exc


def _required_lifecycle(
    value: Any,
    *,
    default: PathLifecycleMode,
    field_name: str,
) -> PathLifecycleMode:
    return _optional_lifecycle(value, field_name=field_name) or default


def _string_list(value: Any, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list | tuple):
        raise PathYamlError(f"'{field_name}' must be a list.")
    items: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise PathYamlError(f"'{field_name}' entries must be non-empty strings.")
        normalized = item.strip().replace("\\", "/").strip("/")
        if normalized in seen:
            raise PathYamlError(f"'{field_name}' contains duplicate entry '{normalized}'.")
        seen.add(normalized)
        items.append(normalized)
    return tuple(items)


def _optional_select(raw: dict[str, Any], *, name: str, mode: PathSelectionMode) -> str:
    value = raw.get(KEY_SELECT)
    if value is None and mode == PathSelectionMode.ONCE:
        return ""
    if not isinstance(value, str) or not value:
        raise PathYamlError(f"'{name}.{KEY_SELECT}' is required and must be a non-empty string.")
    return value


def _string(value: Any, *, default: str, field_name: str) -> str:
    if value is None:
        return default
    if not isinstance(value, str):
        raise PathYamlError(f"'{field_name}' must be a string.")
    return value


def _non_empty_string(value: Any, *, default: str, field_name: str) -> str:
    result = _string(value, default=default, field_name=field_name)
    if not result.strip():
        raise PathYamlError(f"'{field_name}' must be a non-empty string.")
    return result.strip()


def _bool(value: Any, *, default: bool, field_name: str) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise PathYamlError(f"'{field_name}' must be a boolean.")
    return value


def _dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise PathYamlError(f"'{field_name}' must be an object.")
    return dict(value)


def _reject_unknown_keys(raw: dict[str, Any], allowed: set[str], *, owner: str) -> None:
    unknown = sorted(str(key) for key in raw if key not in allowed)
    if not unknown:
        return
    allowed_text = ", ".join(sorted(allowed))
    unknown_text = ", ".join(unknown)
    raise PathYamlError(
        f"Unknown key(s) in '{owner}': {unknown_text}. Allowed keys: {allowed_text}."
    )
