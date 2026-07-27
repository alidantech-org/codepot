from __future__ import annotations

from codepotg.api import CancellationToken
from codepotg.ir import Contract, Name

from ..diagnostics import DiagnosticBag
from ..options import OpenApiOptions, XCodegenPolicy
from ..parsing.document import ParsedDocument
from ..references.resolver import ReferenceResolver
from .context import NormalizationContext
from .groups import HTTP_METHODS, prepare_groups
from .identities import stable_id
from .operations import normalize_operations
from .provenance import extension_values, kernel_data, selected_raw
from .schemas import materialize_components


def normalize_standard_contract(
    *,
    root: ParsedDocument,
    resolver: ReferenceResolver,
    options: OpenApiOptions,
    diagnostics: DiagnosticBag,
    cancellation: CancellationToken,
) -> Contract | None:
    cancellation.raise_if_cancelled()
    if not _handle_unimplemented_x_codegen(root, options, diagnostics):
        return None
    _diagnose_unimplemented_security(root, diagnostics)

    context = NormalizationContext(
        root=root,
        resolver=resolver,
        options=options,
        diagnostics=diagnostics,
        cancellation=cancellation,
        x_codegen=None,
    )
    prepare_groups(context)
    cancellation.raise_if_cancelled()
    materialize_components(context)
    cancellation.raise_if_cancelled()
    normalize_operations(context)
    cancellation.raise_if_cancelled()
    if not context.groups:
        context.ensure_group("default", pointer="")

    info = root.value.get("info")
    if not isinstance(info, dict):
        diagnostics.error(
            "OA_STRUCTURE_INFO",
            "OpenAPI root requires an info object",
            span=root.span("/info") or root.span(""),
        )
        return None
    title = info.get("title")
    version = info.get("version")
    if not isinstance(title, str) or not title.strip():
        diagnostics.error(
            "OA_STRUCTURE_INFO_FIELD",
            "OpenAPI info.title must be a non-empty string",
            span=root.span("/info/title") or root.span("/info"),
        )
        return None
    if not isinstance(version, str) or not version.strip():
        diagnostics.error(
            "OA_STRUCTURE_INFO_FIELD",
            "OpenAPI info.version must be a non-empty string",
            span=root.span("/info/version") or root.span("/info"),
        )
        return None

    contract_id = stable_id(
        source=root.source.logical_id,
        category="contract",
        pointer="",
        hint=title,
    )
    return Contract(
        id=contract_id,
        name=Name(title),
        groups=context.freeze_groups(),
        version=version,
        data=kernel_data(
            root,
            "",
            options=options,
            diagnostics=diagnostics,
            raw={
                "openapi": root.openapi_version,
                **selected_raw(root.value, "externalDocs", "servers", "security", "tags"),
            },
            extensions=(
                extension_values(root.value) if options.preserve_unknown_extensions else {}
            ),
        ),
    )


def _handle_unimplemented_x_codegen(
    root: ParsedDocument,
    options: OpenApiOptions,
    diagnostics: DiagnosticBag,
) -> bool:
    if "x-codegen" not in root.value:
        return True
    if options.x_codegen_policy is XCodegenPolicy.TOLERANT:
        diagnostics.warning(
            "OA_XCODEGEN_NOT_IMPLEMENTED",
            "typed x-codegen normalization is not implemented; metadata was ignored",
            span=root.span("/x-codegen"),
            details=(("task", "OA-010"),),
        )
        return True
    diagnostics.error(
        "OA_XCODEGEN_NOT_IMPLEMENTED",
        "typed x-codegen normalization is not implemented",
        span=root.span("/x-codegen"),
        details=(("policy", options.x_codegen_policy.value), ("task", "OA-010")),
    )
    return False


def _diagnose_unimplemented_security(
    root: ParsedDocument,
    diagnostics: DiagnosticBag,
) -> None:
    pointer = _first_security_pointer(root.value)
    if pointer is None:
        return
    diagnostics.warning(
        "OA_SECURITY_NOT_IMPLEMENTED",
        "OpenAPI security and access normalization is not implemented; declarations were preserved only as source metadata",
        span=root.span(pointer),
        details=(("task", "OA-009"),),
    )


def _first_security_pointer(value: dict[str, object]) -> str | None:
    if "security" in value:
        return "/security"
    components = value.get("components")
    if isinstance(components, dict) and "securitySchemes" in components:
        return "/components/securitySchemes"
    paths = value.get("paths")
    if not isinstance(paths, dict):
        return None
    for path_name in sorted(paths):
        path_item = paths[path_name]
        if not isinstance(path_item, dict):
            continue
        escaped_path = path_name.replace("~", "~0").replace("/", "~1")
        for method in HTTP_METHODS:
            operation = path_item.get(method)
            if isinstance(operation, dict) and "security" in operation:
                return f"/paths/{escaped_path}/{method}/security"
    return None
