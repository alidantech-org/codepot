from __future__ import annotations

import json
import math
from dataclasses import fields, is_dataclass
from enum import Enum
from importlib import import_module
from typing import Any

import yaml

from codepotg.diagnostics import Diagnostics
from codepotg.domain.ir import Contract, Name, SemanticId, validate_contract
from codepotg.versions import IR_API_VERSION

public_ir = import_module("codepotg.domain.ir")
public_diagnostics = import_module("codepotg.diagnostics")

_FORMAT = "codepot-ir"


class IrCodecError(ValueError):
    def __init__(self, code: str, message: str, *, path: str = "$") -> None:
        super().__init__(f"{path}: {message}")
        self.code = code
        self.message = message
        self.path = path


def contract_to_document(contract: Contract) -> dict[str, object]:
    diagnostics = validate_contract(contract)
    if diagnostics.has_errors:
        first = diagnostics.errors[0]
        raise IrCodecError(first.code, first.message, path="$.contract")
    return {
        "contract": _encode(contract),
        "format": _FORMAT,
        "irVersion": str(IR_API_VERSION),
    }


def contract_to_json(contract: Contract, *, pretty: bool = True) -> str:
    document = contract_to_document(contract)
    return json.dumps(
        document,
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        sort_keys=True,
    ) + ("\n" if pretty else "")


def contract_to_yaml(contract: Contract) -> str:
    return yaml.safe_dump(
        contract_to_document(contract),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=True,
    )


def contract_from_document(document: object) -> Contract:
    if not isinstance(document, dict):
        raise IrCodecError("IR_CODEC_ROOT", "IR transport root must be an object")
    unknown = sorted(set(document) - {"contract", "format", "irVersion"})
    if unknown:
        raise IrCodecError(
            "IR_CODEC_UNKNOWN_FIELD",
            f"unknown transport field {unknown[0]!r}",
        )
    if document.get("format") != _FORMAT:
        raise IrCodecError("IR_CODEC_FORMAT", "unsupported IR transport format")
    if document.get("irVersion") != str(IR_API_VERSION):
        raise IrCodecError(
            "IR_CODEC_VERSION",
            f"IR transport requires version {IR_API_VERSION}",
        )
    value = _decode(document.get("contract"), path="$.contract")
    if not isinstance(value, Contract):
        raise IrCodecError("IR_CODEC_CONTRACT", "transport does not contain a Contract")
    diagnostics = validate_contract(value)
    if diagnostics.has_errors:
        first = diagnostics.errors[0]
        raise IrCodecError(first.code, first.message, path="$.contract")
    return value


def contract_from_json(value: str | bytes) -> Contract:
    try:
        text = value.decode("utf-8") if isinstance(value, bytes) else value
        document = json.loads(text, object_pairs_hook=_json_pairs)
    except UnicodeDecodeError as exc:
        raise IrCodecError("IR_CODEC_UTF8", "IR JSON must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise IrCodecError(
            "IR_CODEC_JSON",
            f"invalid JSON at line {exc.lineno}, column {exc.colno}",
        ) from exc
    return contract_from_document(document)


def contract_from_yaml(value: str | bytes) -> Contract:
    try:
        text = value.decode("utf-8") if isinstance(value, bytes) else value
        document = yaml.load(text, Loader=_UniqueKeyLoader)
    except UnicodeDecodeError as exc:
        raise IrCodecError("IR_CODEC_UTF8", "IR YAML must be UTF-8") from exc
    except yaml.YAMLError as exc:
        raise IrCodecError("IR_CODEC_YAML", "IR YAML syntax is invalid") from exc
    return contract_from_document(document)


def validate_transport(document: object) -> Diagnostics:
    try:
        contract_from_document(document)
    except IrCodecError as exc:
        from codepotg.diagnostics import Diagnostic, DiagnosticSeverity

        return Diagnostics(
            (
                Diagnostic(
                    code=exc.code,
                    severity=DiagnosticSeverity.ERROR,
                    message=exc.message,
                    details=(("path", exc.path),),
                ),
            )
        )
    return Diagnostics()


def _encode(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise IrCodecError("IR_CODEC_NUMBER", "non-finite numbers are not supported")
        return value
    if isinstance(value, SemanticId):
        return {"$ref": value.value}
    if isinstance(value, Name):
        return {"$name": value.value}
    if isinstance(value, Enum):
        return {"$enum": type(value).__name__, "value": value.value}
    if isinstance(value, tuple | list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        result: dict[str, object] = {}
        for key in sorted(value):
            if not isinstance(key, str):
                raise IrCodecError("IR_CODEC_KEY", "object keys must be strings")
            result[key] = _encode(value[key])
        return result
    if is_dataclass(value):
        result = {"$type": type(value).__name__}
        for item in fields(value):
            if not item.init or item.name.startswith("_"):
                continue
            result[item.name] = _encode(getattr(value, item.name))
        return result
    raise IrCodecError(
        "IR_CODEC_VALUE",
        f"unsupported IR value {type(value).__name__}",
    )


def _decode(value: object, *, path: str) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise IrCodecError("IR_CODEC_NUMBER", "non-finite numbers are not supported", path=path)
        return value
    if isinstance(value, list):
        return tuple(
            _decode(item, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        )
    if not isinstance(value, dict):
        raise IrCodecError(
            "IR_CODEC_VALUE",
            f"unsupported decoded value {type(value).__name__}",
            path=path,
        )

    if "$ref" in value:
        if set(value) != {"$ref"} or not isinstance(value["$ref"], str):
            raise IrCodecError("IR_CODEC_REF", "invalid semantic reference", path=path)
        return SemanticId(value["$ref"])
    if "$name" in value:
        if set(value) != {"$name"} or not isinstance(value["$name"], str):
            raise IrCodecError("IR_CODEC_NAME", "invalid semantic name", path=path)
        return Name(value["$name"])
    if "$enum" in value:
        if set(value) != {"$enum", "value"}:
            raise IrCodecError("IR_CODEC_ENUM", "invalid enum document", path=path)
        enum_name = value["$enum"]
        if not isinstance(enum_name, str):
            raise IrCodecError("IR_CODEC_ENUM", "enum type must be a string", path=path)
        enum_type = _enum_registry().get(enum_name)
        if enum_type is None:
            raise IrCodecError(
                "IR_CODEC_ENUM",
                f"unknown IR enum {enum_name!r}",
                path=path,
            )
        try:
            return enum_type(value["value"])
        except (TypeError, ValueError) as exc:
            raise IrCodecError("IR_CODEC_ENUM", "invalid enum value", path=path) from exc
    if "$type" in value:
        type_name = value["$type"]
        if not isinstance(type_name, str):
            raise IrCodecError("IR_CODEC_TYPE", "IR type must be a string", path=path)
        target = _type_registry().get(type_name)
        if target is None:
            raise IrCodecError(
                "IR_CODEC_TYPE",
                f"unknown IR record type {type_name!r}",
                path=path,
            )
        allowed = {
            item.name
            for item in fields(target)
            if item.init and not item.name.startswith("_")
        }
        unknown = sorted(set(value) - allowed - {"$type"})
        if unknown:
            raise IrCodecError(
                "IR_CODEC_UNKNOWN_FIELD",
                f"unknown {type_name} field {unknown[0]!r}",
                path=path,
            )
        kwargs = {
            key: _decode(item, path=f"{path}.{key}")
            for key, item in value.items()
            if key != "$type"
        }
        try:
            return target(**kwargs)
        except (TypeError, ValueError) as exc:
            raise IrCodecError(
                "IR_CODEC_CONSTRUCTION",
                f"invalid {type_name} record",
                path=path,
            ) from exc

    return {
        key: _decode(item, path=f"{path}.{key}")
        for key, item in sorted(value.items())
    }


def _type_registry() -> dict[str, type[Any]]:
    result: dict[str, type[Any]] = {}
    for module in (public_ir, public_diagnostics):
        for name in getattr(module, "__all__", ()):
            candidate = getattr(module, name, None)
            if isinstance(candidate, type) and is_dataclass(candidate):
                result[candidate.__name__] = candidate
    return result


def _enum_registry() -> dict[str, type[Enum]]:
    result: dict[str, type[Enum]] = {}
    for module in (public_ir, public_diagnostics):
        for name in getattr(module, "__all__", ()):
            candidate = getattr(module, name, None)
            if isinstance(candidate, type) and issubclass(candidate, Enum):
                result[candidate.__name__] = candidate
    return result


def _json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise IrCodecError("IR_CODEC_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = value
    return result


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _yaml_mapping(
    loader: _UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise IrCodecError("IR_CODEC_KEY", "YAML mapping keys must be strings")
        if key in result:
            raise IrCodecError("IR_CODEC_DUPLICATE_KEY", f"duplicate key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _yaml_mapping,
)
