from __future__ import annotations

from codepotg.ir import Name, SchemaUse

from ..parsing.document import ParsedDocument
from ..references.pointer import join_pointer
from .context import NormalizationContext, OperationBuilder
from .operation_support import (
    resolve_mapping,
    schema_from_content,
    schema_from_content_with_media,
    schema_id_for_use,
    title,
)
from .provenance import kernel_data, selected_raw


def normalize_parameters(
    context: NormalizationContext,
    operation: OperationBuilder,
    *,
    document: ParsedDocument,
    pointer: str,
    group: str,
    path_parameters: object,
    operation_parameters: object,
) -> None:
    merged: dict[tuple[str, str], tuple[ParsedDocument, str, dict[str, object]]] = {}
    for raw_collection, collection_pointer in (
        (path_parameters, pointer.rsplit("/", 1)[0] + "/parameters"),
        (operation_parameters, join_pointer(pointer, "parameters")),
    ):
        if raw_collection is None:
            continue
        if not isinstance(raw_collection, list):
            context.diagnostics.error(
                "OA_OPERATION_PARAMETERS",
                "parameters must be an array",
                span=document.span(collection_pointer),
            )
            continue
        for index, raw in enumerate(raw_collection):
            item_pointer = join_pointer(collection_pointer, index)
            resolved = resolve_mapping(
                context,
                document=document,
                pointer=item_pointer,
                raw=raw,
                expected="parameter",
            )
            if resolved is None:
                continue
            item_document, target_pointer, parameter = resolved
            name = parameter.get("name")
            location = parameter.get("in")
            if not isinstance(name, str) or not isinstance(location, str):
                context.diagnostics.error(
                    "OA_OPERATION_PARAMETER_SHAPE",
                    "parameter requires string name and in fields",
                    span=item_document.span(target_pointer),
                )
                continue
            merged[(name, location)] = (item_document, target_pointer, parameter)

    used_names: set[str] = set()
    for (name, location), (item_document, item_pointer, parameter) in merged.items():
        schema = parameter.get("schema")
        schema_pointer = join_pointer(item_pointer, "schema")
        if not isinstance(schema, dict):
            content = parameter.get("content")
            schema, schema_pointer = schema_from_content(
                context,
                document=item_document,
                pointer=join_pointer(item_pointer, "content"),
                content=content,
                owner=f"parameter {name!r}",
            )
        if not isinstance(schema, dict):
            context.diagnostics.error(
                "OA_OPERATION_PARAMETER_SCHEMA",
                f"parameter {name!r} has no schema",
                span=item_document.span(item_pointer),
            )
            continue
        schema_id = schema_id_for_use(
            context,
            document=item_document,
            pointer=schema_pointer,
            schema=schema,
            hint=f"{operation.name.value}{title(name)}Input",
            group=group,
        )
        input_name = name if name not in used_names else f"{name}_{location}"
        used_names.add(input_name)
        operation.inputs.append(
            SchemaUse(
                name=Name(input_name),
                schema=schema_id,
                required=parameter.get("required") is True or location == "path",
                nullable=parameter.get("nullable") is True,
                readonly=False,
                data=kernel_data(
                    item_document,
                    item_pointer,
                    options=context.options,
                    diagnostics=context.diagnostics,
                    raw={
                        "http": {
                            "in": location,
                            "name": name,
                            **selected_raw(parameter, "allowEmptyValue", "explode", "style"),
                        }
                    },
                ),
            )
        )
        context.diagnostics.warning(
            "OA_UNSUPPORTED_HTTP_PARAMETER_BINDING",
            f"HTTP {location} binding for parameter {name!r} is preserved on the input but not represented by the current public HttpFacet",
            span=item_document.span(item_pointer),
            details=(("coreBlocker", "HttpFacet parameter bindings"),),
        )


def normalize_request_body(
    context: NormalizationContext,
    operation: OperationBuilder,
    *,
    document: ParsedDocument,
    pointer: str,
    group: str,
    raw: object,
) -> None:
    if raw is None:
        return
    body_pointer = join_pointer(pointer, "requestBody")
    resolved = resolve_mapping(
        context,
        document=document,
        pointer=body_pointer,
        raw=raw,
        expected="requestBody",
    )
    if resolved is None:
        return
    item_document, item_pointer, body = resolved
    schema, schema_pointer, media_types = schema_from_content_with_media(
        context,
        document=item_document,
        pointer=join_pointer(item_pointer, "content"),
        content=body.get("content"),
        owner="request body",
    )
    if schema is None:
        context.diagnostics.error(
            "OA_OPERATION_REQUEST_BODY_SCHEMA",
            "request body has no representable content schema",
            span=item_document.span(item_pointer),
        )
        return
    schema_id = schema_id_for_use(
        context,
        document=item_document,
        pointer=schema_pointer,
        schema=schema,
        hint=f"{operation.name.value}BodyInput",
        group=group,
    )
    existing_names = {item.name.raw.original for item in operation.inputs}
    body_name = "body" if "body" not in existing_names else "requestBody"
    operation.inputs.append(
        SchemaUse(
            name=Name(body_name),
            schema=schema_id,
            required=body.get("required") is True,
            data=kernel_data(
                item_document,
                item_pointer,
                options=context.options,
                diagnostics=context.diagnostics,
                raw={"http": {"mediaTypes": list(media_types)}},
            ),
        )
    )
    if media_types:
        context.diagnostics.warning(
            "OA_UNSUPPORTED_HTTP_REQUEST_MEDIA",
            "request media types are preserved on the input but not represented by the current public HttpFacet",
            span=item_document.span(join_pointer(item_pointer, "content")),
            details=(("coreBlocker", "HttpFacet request media types"),),
        )
