from __future__ import annotations

import re

from codepotg.ir import SemanticId

from ..parsing.document import ParsedDocument
from ..references.identity import ReferenceIdentity
from ..references.pointer import join_pointer
from .context import NormalizationContext
from .schemas import materialize_schema

_OPERATION_NAME = re.compile(r"[^A-Za-z0-9]+")


def schema_from_content(
    context: NormalizationContext,
    *,
    document: ParsedDocument,
    pointer: str,
    content: object,
    owner: str,
) -> tuple[dict[str, object] | None, str]:
    schema, schema_pointer, _ = schema_from_content_with_media(
        context,
        document=document,
        pointer=pointer,
        content=content,
        owner=owner,
    )
    return schema, schema_pointer


def schema_from_content_with_media(
    context: NormalizationContext,
    *,
    document: ParsedDocument,
    pointer: str,
    content: object,
    owner: str,
    allow_empty: bool = False,
) -> tuple[dict[str, object] | None, str, tuple[str, ...]]:
    if content is None and allow_empty:
        return None, pointer, ()
    if not isinstance(content, dict) or not content:
        if not allow_empty:
            context.diagnostics.error(
                "OA_OPERATION_CONTENT",
                f"{owner} content must be a non-empty object",
                span=document.span(pointer),
            )
        return None, pointer, ()
    media_types = tuple(sorted(content))
    selected = media_types[0]
    if len(media_types) > 1:
        context.diagnostics.warning(
            "OA_UNSUPPORTED_HTTP_MEDIA_ALTERNATIVES",
            f"{owner} declares multiple media types; {selected!r} supplies the neutral schema and all alternatives remain preserved",
            span=document.span(pointer),
            details=(("mediaTypes", media_types),),
        )
    media = content[selected]
    media_pointer = join_pointer(pointer, selected)
    if not isinstance(media, dict) or not isinstance(media.get("schema"), dict):
        return None, join_pointer(media_pointer, "schema"), media_types
    return media["schema"], join_pointer(media_pointer, "schema"), media_types


def schema_id_for_use(
    context: NormalizationContext,
    *,
    document: ParsedDocument,
    pointer: str,
    schema: dict[str, object],
    hint: str,
    group: str,
) -> SemanticId:
    reference = schema.get("$ref")
    if isinstance(reference, str):
        target = context.resolver.resolve(
            document=document,
            reference=reference,
            expected="schema",
            source_identity=ReferenceIdentity(document.source.canonical_id, pointer),
        )
        if target is not None and isinstance(target.value, dict):
            target_hint = ref_hint(target.identity.pointer, hint)
            owner = "shared"
            if target.document is context.root and target.identity.pointer.startswith(
                "/components/schemas/"
            ):
                owner = (
                    context.x_codegen.schema(target_hint).group
                    if context.x_codegen
                    and context.x_codegen.schema(target_hint)
                    and context.x_codegen.schema(target_hint).group
                    else "shared"
                )
            return materialize_schema(
                context,
                document=target.document,
                pointer=target.identity.pointer,
                value=target.value,
                hint=target_hint,
                group=owner,
            )
    return materialize_schema(
        context,
        document=document,
        pointer=pointer,
        value=schema,
        hint=hint,
        group=group,
    )


def resolve_mapping(
    context: NormalizationContext,
    *,
    document: ParsedDocument,
    pointer: str,
    raw: object,
    expected: str,
) -> tuple[ParsedDocument, str, dict[str, object]] | None:
    if not isinstance(raw, dict):
        context.diagnostics.error(
            "OA_REF_INCOMPATIBLE_TARGET",
            f"{expected} must be an object",
            span=document.span(pointer),
        )
        return None
    reference = raw.get("$ref")
    if not isinstance(reference, str):
        return document, pointer, raw
    resolved = context.resolver.resolve(
        document=document,
        reference=reference,
        expected=expected,
        source_identity=ReferenceIdentity(document.source.canonical_id, pointer),
    )
    if resolved is None or not isinstance(resolved.value, dict):
        return None
    return resolved.document, resolved.identity.pointer, resolved.value


def title(value: str) -> str:
    return "".join(
        part[:1].upper() + part[1:]
        for part in _OPERATION_NAME.split(value)
        if part
    )


def ref_hint(pointer: str, fallback: str) -> str:
    if not pointer:
        return fallback
    return pointer.rsplit("/", 1)[-1].replace("~1", "/").replace("~0", "~") or fallback
