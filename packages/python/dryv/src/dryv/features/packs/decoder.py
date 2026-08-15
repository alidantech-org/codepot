from __future__ import annotations

from typing import Any

from .model import (
    BindingDefinition,
    FrozenObject,
    FrozenValue,
    NormalizedPack,
    OptionDefinition,
    PackConfigurationError,
    PackManifest,
    PackTemplateResource,
    SelectionConfig,
)

_ROOT_FIELDS = {
    "apiVersion", "id", "version", "description", "requires", "include", "exclude",
    "options", "bindings", "selections", "executables", "commands",
}


def decode_pack_manifest(value: object) -> PackManifest:
    root = _object(value, "$")
    _unknown(root, _ROOT_FIELDS, "$")

    options: list[OptionDefinition] = []
    for name, raw in sorted(_object(root.get("options", {}), "$.options").items()):
        if isinstance(raw, dict):
            _unknown(raw, {"default", "choices", "required", "description"}, f"$.options.{name}")
            choices = tuple(_freeze(item, f"$.options.{name}.choices") for item in _list(raw.get("choices", []), f"$.options.{name}.choices"))
            default = _freeze(raw.get("default"), f"$.options.{name}.default")
            required = _bool(raw.get("required", False), f"$.options.{name}.required")
            description = _optional_string(raw.get("description"), f"$.options.{name}.description")
        else:
            choices, default, required, description = (), _freeze(raw, f"$.options.{name}"), False, None
        options.append(OptionDefinition(name, default, choices, required, description))

    bindings: list[BindingDefinition] = []
    for name, raw in sorted(_object(root.get("bindings", {}), "$.bindings").items()):
        item = _object(raw, f"$.bindings.{name}")
        _unknown(item, {"required", "description"}, f"$.bindings.{name}")
        bindings.append(BindingDefinition(name, _bool(item.get("required", False), f"$.bindings.{name}.required"), _optional_string(item.get("description"), f"$.bindings.{name}.description")))

    selections: list[SelectionConfig] = []
    for key, raw in sorted(_object(root.get("selections", {}), "$.selections").items()):
        item = _object(raw, f"$.selections.{key}")
        _unknown(item, {"paths", "select", "imports", "exports", "bindings", "symbols"}, f"$.selections.{key}")
        imports = tuple(sorted(
            (name, _string(target, f"$.selections.{key}.imports.{name}"))
            for name, target in _object(item.get("imports", {}), f"$.selections.{key}.imports").items()
        ))
        selections.append(SelectionConfig(
            key=key,
            paths=tuple(_string(part, f"$.selections.{key}.paths") for part in _list(item.get("paths", []), f"$.selections.{key}.paths")),
            select=_optional_string(item.get("select"), f"$.selections.{key}.select"),
            imports=imports,
            exports=tuple(_string(part, f"$.selections.{key}.exports") for part in _list(item.get("exports", []), f"$.selections.{key}.exports")),
            bindings=tuple(_string(part, f"$.selections.{key}.bindings") for part in _list(item.get("bindings", []), f"$.selections.{key}.bindings")),
            symbols=tuple(_string(part, f"$.selections.{key}.symbols") for part in _list(item.get("symbols", []), f"$.selections.{key}.symbols")),
        ))

    return PackManifest(
        api_version=_string(root.get("apiVersion"), "$.apiVersion"),
        id=_string(root.get("id"), "$.id"),
        version=_string(root.get("version"), "$.version"),
        description=_optional_string(root.get("description"), "$.description"),
        include=tuple(_string(item, "$.include") for item in _list(root.get("include", ["**/*"]), "$.include")),
        exclude=tuple(_string(item, "$.exclude") for item in _list(root.get("exclude", []), "$.exclude")),
        options=tuple(options),
        bindings=tuple(bindings),
        selections=tuple(selections),
        requires=_freeze_object(root.get("requires", {}), "$.requires"),
        executables=_freeze_object(root.get("executables", {}), "$.executables"),
        commands=_freeze_object(root.get("commands", {}), "$.commands"),
    )


def normalize_pack(manifest: PackManifest, templates: tuple[PackTemplateResource, ...]) -> NormalizedPack:
    return NormalizedPack(manifest, tuple(sorted(templates, key=lambda item: item.resource_id)))


def _freeze(value: object, path: str) -> FrozenValue:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, list):
        return tuple(_freeze(item, path) for item in value)
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise PackConfigurationError("PACK_NON_STRING_KEY", "mapping keys must be strings", path=path)
        return tuple((key, _freeze(value[key], f"{path}.{key}")) for key in sorted(value))
    raise PackConfigurationError("PACK_VALUE", f"unsupported configuration value {type(value).__name__}", path=path)


def _freeze_object(value: object, path: str) -> FrozenObject:
    frozen = _freeze(value, path)
    if not isinstance(frozen, tuple) or (frozen and not all(isinstance(item, tuple) and len(item) == 2 for item in frozen)):
        raise PackConfigurationError("PACK_EXPECTED_OBJECT", "expected an object", path=path)
    return frozen  # type: ignore[return-value]


def _object(value: object, path: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise PackConfigurationError("PACK_EXPECTED_OBJECT", "expected an object with string keys", path=path)
    return value


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise PackConfigurationError("PACK_EXPECTED_LIST", "expected a list", path=path)
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise PackConfigurationError("PACK_EXPECTED_STRING", "expected a non-empty trimmed string", path=path)
    return value


def _optional_string(value: object, path: str) -> str | None:
    return None if value is None else _string(value, path)


def _bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise PackConfigurationError("PACK_EXPECTED_BOOLEAN", "expected a boolean", path=path)
    return value


def _unknown(value: dict[str, object], allowed: set[str], path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise PackConfigurationError("PACK_UNKNOWN_FIELD", f"unknown field {unknown[0]!r}", path=path)


__all__ = ["decode_pack_manifest", "normalize_pack"]
