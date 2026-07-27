from __future__ import annotations

import re

from codepotg.ir import HttpFacet, Name, OperationFacets

from ..options import OperationIdPolicy
from ..parsing.document import ParsedDocument
from ..references.identity import ReferenceIdentity
from ..references.pointer import join_pointer
from .context import NormalizationContext, OperationBuilder
from .groups import HTTP_METHODS, operation_group
from .identities import stable_id
from .operation_inputs import normalize_parameters, normalize_request_body
from .operation_responses import normalize_responses
from .provenance import extension_values, kernel_data, selected_raw


_OPERATION_NAME = re.compile(r"[^A-Za-z0-9]+")


def normalize_operations(context: NormalizationContext) -> None:
    paths = context.root.value.get("paths", {})
    if not isinstance(paths, dict):
        return
    for path in sorted(paths):
        context.cancellation.raise_if_cancelled()
        raw_path_item = paths[path]
        path_pointer = join_pointer("/paths", path)
        path_document = context.root
        path_item = raw_path_item
        if isinstance(path_item, dict) and isinstance(path_item.get("$ref"), str):
            resolved = context.resolver.resolve(
                document=context.root,
                reference=path_item["$ref"],
                expected="mapping",
                source_identity=ReferenceIdentity(context.root.source.canonical_id, path_pointer),
            )
            if resolved is not None:
                path_document = resolved.document
                path_pointer = resolved.identity.pointer
                path_item = resolved.value
        if not isinstance(path_item, dict):
            context.diagnostics.error(
                "OA_OPERATION_PATH_ITEM",
                f"path item {path!r} must be an object",
                span=context.root.span(path_pointer),
            )
            continue
        path_parameters = path_item.get("parameters", [])
        for method in HTTP_METHODS:
            operation_value = path_item.get(method)
            if operation_value is None:
                continue
            operation_pointer = join_pointer(path_pointer, method)
            if not isinstance(operation_value, dict):
                context.diagnostics.error(
                    "OA_OPERATION_SHAPE",
                    f"{method.upper()} {path} operation must be an object",
                    span=path_document.span(operation_pointer),
                )
                continue
            _normalize_operation(
                context,
                document=path_document,
                path=path,
                method=method,
                pointer=operation_pointer,
                value=operation_value,
                path_parameters=path_parameters,
            )


def _normalize_operation(
    context: NormalizationContext,
    *,
    document: ParsedDocument,
    path: str,
    method: str,
    pointer: str,
    value: dict[str, object],
    path_parameters: object,
) -> None:
    operation_id_raw = value.get("operationId")
    operation_id = (
        operation_id_raw
        if isinstance(operation_id_raw, str) and operation_id_raw
        else None
    )
    fallback = _fallback_operation_id(method, path)
    if operation_id is None:
        severity_message = f"operation {method.upper()} {path} has no operationId"
        if context.options.operation_ids is OperationIdPolicy.REQUIRE:
            context.diagnostics.error(
                "OA_OPERATION_ID_REQUIRED",
                severity_message,
                span=document.span(pointer),
            )
        else:
            context.diagnostics.warning(
                "OA_OPERATION_ID_FALLBACK",
                f"{severity_message}; using deterministic id {fallback!r}",
                span=document.span(pointer),
            )
        operation_id = fallback
    metadata = context.x_codegen.operation(operation_id) if context.x_codegen else None
    if metadata is None and context.x_codegen is not None:
        metadata = context.x_codegen.operation(f"{method.upper()} {path}")
    group = operation_group(
        context,
        value,
        operation_key=operation_id,
        method=method,
        path=path,
        pointer=pointer,
    )
    semantic_id = stable_id(
        source=document.source.logical_id,
        category="operation",
        pointer=pointer,
        hint=operation_id,
        explicit=metadata.id if metadata else None,
    )
    raw_http: dict[str, object] = {
        "method": method.upper(),
        "path": path,
    }
    if "servers" in value:
        raw_http["servers"] = value["servers"]
        context.diagnostics.warning(
            "OA_UNSUPPORTED_HTTP_SERVERS",
            "operation servers are not represented by the current public HttpFacet",
            span=document.span(join_pointer(pointer, "servers")),
            details=(("coreBlocker", "HttpFacet.servers"),),
        )
    builder = OperationBuilder(
        id=semantic_id,
        name=Name(operation_id),
        facets=OperationFacets(
            http=HttpFacet(method=method.upper(), path=path, operation_id=operation_id)
        ),
        data=kernel_data(
            document,
            pointer,
            options=context.options,
            diagnostics=context.diagnostics,
            raw={
                **selected_raw(value, "deprecated", "description", "externalDocs", "summary"),
                "http": raw_http,
            },
            extensions=(
                extension_values(value) if context.options.preserve_unknown_extensions else {}
            ),
        ),
    )
    normalize_parameters(
        context,
        builder,
        document=document,
        pointer=pointer,
        group=group,
        path_parameters=path_parameters,
        operation_parameters=value.get("parameters", []),
    )
    normalize_request_body(
        context,
        builder,
        document=document,
        pointer=pointer,
        group=group,
        raw=value.get("requestBody"),
    )
    normalize_responses(
        context,
        builder,
        document=document,
        pointer=pointer,
        group=group,
        raw=value.get("responses"),
    )
    context.add_operation(
        group,
        builder,
        document,
        pointer,
        keys=(operation_id, fallback, f"{method.upper()} {path}"),
    )


def _fallback_operation_id(method: str, path: str) -> str:
    normalized = _OPERATION_NAME.sub("_", path.strip("/{}")).strip("_").lower()
    return f"{method.lower()}_{normalized or 'root'}"
