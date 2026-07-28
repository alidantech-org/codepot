from __future__ import annotations

from collections.abc import Callable
from typing import cast

import yaml
from dryv.ir import (
    Contract,
    contract_from_document,
    contract_from_json,
    contract_from_yaml,
    contract_to_document,
    contract_to_json,
    contract_to_yaml,
)
from dryv.versions import IR_API_VERSION
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode, Node

FORMAT = "codepot-ir"
VERSION = str(IR_API_VERSION)

Constructor = Callable[..., object]


class DuplicateSafeLoader(yaml.SafeLoader):
    """Compatibility loader that rejects duplicate YAML mapping keys."""


def _construct_object(loader: DuplicateSafeLoader, node: Node, *, deep: bool) -> object:
    constructor = cast(Constructor, loader.construct_object)
    return constructor(node, deep=deep)


def _construct_mapping(
    loader: DuplicateSafeLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[object, object]:
    loader.flatten_mapping(node)
    result: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = _construct_object(loader, key_node, deep=deep)
        if key in result:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        result[key] = _construct_object(loader, value_node, deep=deep)
    return result


DuplicateSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def to_document(contract: Contract) -> dict[str, object]:
    """Return the core-owned canonical IR document."""

    return contract_to_document(contract)


def from_document(document: object) -> Contract:
    """Decode a core-owned canonical IR document."""

    return contract_from_document(document)


def dumps_json(contract: Contract) -> str:
    """Encode canonical compact JSON for authoring transport compatibility."""

    return contract_to_json(contract, pretty=False)


def loads_json(value: str | bytes) -> Contract:
    return contract_from_json(value)


def dumps_yaml(contract: Contract) -> str:
    return contract_to_yaml(contract)


def loads_yaml(value: str | bytes) -> Contract:
    return contract_from_yaml(value)
