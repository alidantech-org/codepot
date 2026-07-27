from __future__ import annotations

import json
from dataclasses import dataclass, field

import yaml
from codepotg.diagnostics import SourceSpan
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

from ..diagnostics import DiagnosticBag
from ..loading.source import LoadedSource
from ..options import OpenApiOptions
from .document import ParsedDocument
from .duplicate_keys import DuplicateKeyError
from .spans import from_marks, root_span
from .structural_validation import validate_structure


class ParseError(ValueError):
    def __init__(self, code: str, message: str, pointer: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.pointer = pointer


@dataclass(slots=True)
class _YamlConversionState:
    max_depth: int
    max_nodes: int
    max_aliases: int
    converted_nodes: int = 0
    alias_expansions: int = 0
    active_nodes: set[int] = field(default_factory=set)
    seen_nodes: set[int] = field(default_factory=set)

    def enter(self, node: Node, depth: int, pointer: str) -> int:
        if depth > self.max_depth:
            raise ParseError(
                "OA_LIMIT_YAML_DEPTH",
                f"YAML conversion depth exceeds maxYamlDepth ({self.max_depth})",
                pointer,
            )
        self.converted_nodes += 1
        if self.converted_nodes > self.max_nodes:
            raise ParseError(
                "OA_LIMIT_YAML_NODES",
                f"YAML conversion exceeds maxYamlNodes ({self.max_nodes})",
                pointer,
            )
        node_id = id(node)
        if node_id in self.active_nodes:
            raise ParseError(
                "OA_PARSE_YAML_ALIAS_CYCLE",
                "recursive YAML alias cycle is not supported",
                pointer,
            )
        if node_id in self.seen_nodes:
            self.alias_expansions += 1
            if self.alias_expansions > self.max_aliases:
                raise ParseError(
                    "OA_LIMIT_YAML_ALIASES",
                    f"YAML alias expansion exceeds maxYamlAliases ({self.max_aliases})",
                    pointer,
                )
        else:
            self.seen_nodes.add(node_id)
        self.active_nodes.add(node_id)
        return node_id

    def leave(self, node_id: int) -> None:
        self.active_nodes.remove(node_id)


class DocumentParser:
    def parse(
        self,
        source: LoadedSource,
        diagnostics: DiagnosticBag,
        *,
        require_openapi: bool = True,
        options: OpenApiOptions | None = None,
    ) -> ParsedDocument | None:
        effective_options = options or OpenApiOptions()
        try:
            text = source.content.decode("utf-8")
        except UnicodeDecodeError:
            diagnostics.error(
                "OA_PARSE_UTF8",
                "source is not valid UTF-8",
                span=None,
            )
            return None

        stripped = text.lstrip()
        try:
            if stripped.startswith(("{", "[")):
                value, spans = _parse_json(text, source)
            else:
                value, spans = _parse_yaml(text, source, effective_options)
        except DuplicateKeyError as exc:
            diagnostics.error(
                "OA_PARSE_DUPLICATE_KEY",
                str(exc),
                span=spans_for_error(source, text),
                details=(("key", exc.key), ("pointer", exc.pointer)),
            )
            return None
        except RecursionError:
            diagnostics.error(
                "OA_LIMIT_YAML_RECURSION",
                "YAML conversion exceeded the safe recursion boundary",
                span=spans_for_error(source, text),
            )
            return None
        except (json.JSONDecodeError, yaml.YAMLError, ParseError, ValueError) as exc:
            code = getattr(exc, "code", "OA_PARSE_INVALID")
            diagnostics.error(code, _safe_error_message(exc), span=spans_for_error(source, text))
            return None

        if not isinstance(value, dict):
            diagnostics.error(
                "OA_STRUCTURE_ROOT",
                "OpenAPI root must be an object",
                span=spans.get(""),
            )
            return None
        version = ""
        if require_openapi:
            validated = validate_structure(value, spans, diagnostics)
            if validated is None:
                return None
            version = validated
        elif isinstance(value.get("openapi"), str):
            version = str(value["openapi"])
        return ParsedDocument.create(
            source=source,
            value=value,
            spans=spans,
            openapi_version=version,
        )


def _parse_json(text: str, source: LoadedSource) -> tuple[object, dict[str, SourceSpan]]:
    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise DuplicateKeyError(key, "")
            result[key] = value
        return result

    value = json.loads(text, object_pairs_hook=hook)
    return value, {"": root_span(source.identity, text)}


def _parse_yaml(
    text: str,
    source: LoadedSource,
    options: OpenApiOptions,
) -> tuple[object, dict[str, SourceSpan]]:
    node = yaml.compose(text, Loader=yaml.SafeLoader)
    if node is None:
        raise ParseError("OA_PARSE_EMPTY", "source document is empty")
    spans: dict[str, SourceSpan] = {}
    state = _YamlConversionState(
        max_depth=options.max_yaml_depth,
        max_nodes=options.max_yaml_nodes,
        max_aliases=options.max_yaml_aliases,
    )
    value = _convert_yaml_node(node, source, "", spans, state, 0)
    return value, spans


def _convert_yaml_node(
    node: Node,
    source: LoadedSource,
    pointer: str,
    spans: dict[str, SourceSpan],
    state: _YamlConversionState,
    depth: int,
) -> object:
    node_id = state.enter(node, depth, pointer)
    try:
        spans[pointer] = from_marks(source.identity, node.start_mark, node.end_mark)
        if isinstance(node, MappingNode):
            result: dict[str, object] = {}
            for key_node, value_node in node.value:
                key_node_id = state.enter(key_node, depth + 1, pointer)
                try:
                    key = _scalar_value(key_node)
                finally:
                    state.leave(key_node_id)
                if not isinstance(key, str):
                    raise ParseError(
                        "OA_PARSE_NON_STRING_KEY",
                        "mapping keys must be strings",
                        pointer,
                    )
                if key in result:
                    raise DuplicateKeyError(key, pointer)
                child_pointer = f"{pointer}/{_escape(key)}"
                result[key] = _convert_yaml_node(
                    value_node,
                    source,
                    child_pointer,
                    spans,
                    state,
                    depth + 1,
                )
            return result
        if isinstance(node, SequenceNode):
            return [
                _convert_yaml_node(
                    item,
                    source,
                    f"{pointer}/{index}",
                    spans,
                    state,
                    depth + 1,
                )
                for index, item in enumerate(node.value)
            ]
        if isinstance(node, ScalarNode):
            return _scalar_value(node)
        raise ParseError(
            "OA_PARSE_NODE",
            f"unsupported YAML node {type(node).__name__}",
            pointer,
        )
    finally:
        state.leave(node_id)


def _scalar_value(node: Node) -> object:
    if not isinstance(node, ScalarNode):
        raise ParseError("OA_PARSE_KEY", "mapping keys must be scalar strings")
    tag = node.tag
    value = node.value
    if tag == "tag:yaml.org,2002:str":
        return value
    if tag == "tag:yaml.org,2002:null":
        return None
    if tag == "tag:yaml.org,2002:bool":
        return value.lower() in {"true", "yes", "on"}
    if tag == "tag:yaml.org,2002:int":
        normalized = value.replace("_", "")
        sign = -1 if normalized.startswith("-") else 1
        normalized = normalized.lstrip("+-")
        if normalized.startswith("0x"):
            return sign * int(normalized[2:], 16)
        if normalized.startswith("0o"):
            return sign * int(normalized[2:], 8)
        if normalized.startswith("0b"):
            return sign * int(normalized[2:], 2)
        return sign * int(normalized, 10)
    if tag == "tag:yaml.org,2002:float":
        parsed = float(value.replace("_", ""))
        if parsed != parsed or parsed in {float("inf"), float("-inf")}:
            raise ParseError("OA_PARSE_NON_FINITE", "non-finite numbers are not supported")
        return parsed
    raise ParseError(
        "OA_PARSE_UNSUPPORTED_SCALAR",
        f"YAML scalar tag {tag!r} is not JSON-compatible",
    )


def _escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _safe_error_message(exc: Exception) -> str:
    if isinstance(exc, json.JSONDecodeError):
        return f"invalid JSON at line {exc.lineno}, column {exc.colno}"
    if isinstance(exc, yaml.MarkedYAMLError) and exc.problem_mark is not None:
        return (
            f"invalid YAML at line {exc.problem_mark.line + 1}, "
            f"column {exc.problem_mark.column + 1}"
        )
    return str(exc) or "invalid source document"


def spans_for_error(source: LoadedSource, text: str) -> SourceSpan:
    return root_span(source.identity, text)
