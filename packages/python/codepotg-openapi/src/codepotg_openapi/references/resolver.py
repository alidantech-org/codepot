from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from codepotg.api import CancellationToken

from ..diagnostics import DiagnosticBag
from ..loading.controlled_loader import SourceLoadingSession, SourceLoadError
from ..options import OpenApiOptions
from ..parsing.document import ParsedDocument
from ..parsing.parser import DocumentParser
from .graph import ReferenceGraph
from .identity import ReferenceIdentity
from .pointer import JsonPointerError, normalize_fragment, resolve_pointer


@dataclass(frozen=True, slots=True)
class ResolvedReference:
    identity: ReferenceIdentity
    document: ParsedDocument
    value: object
    original: str
    cycle: bool = False


@dataclass(frozen=True, slots=True)
class ResolverStats:
    parse_counts: tuple[tuple[str, int], ...]
    resolution_counts: tuple[tuple[str, int], ...]


class ReferenceResolver:
    def __init__(
        self,
        *,
        root: ParsedDocument,
        loader: SourceLoadingSession,
        parser: DocumentParser,
        options: OpenApiOptions,
        diagnostics: DiagnosticBag,
        cancellation: CancellationToken,
        instrumentation: Callable[[str, str], None] | None = None,
    ) -> None:
        self.root = root
        self._loader = loader
        self._parser = parser
        self._options = options
        self._diagnostics = diagnostics
        self._cancellation = cancellation
        self._instrumentation = instrumentation
        self._documents: dict[str, ParsedDocument] = {root.source.canonical_id: root}
        self._cache: dict[ReferenceIdentity, ResolvedReference] = {}
        self._parse_counts: dict[str, int] = {root.source.canonical_id: 1}
        self._resolution_counts: dict[str, int] = {}
        self._graph = ReferenceGraph()

    @property
    def documents(self) -> tuple[ParsedDocument, ...]:
        return tuple(sorted(self._documents.values(), key=lambda item: item.source.logical_id))

    @property
    def stats(self) -> ResolverStats:
        return ResolverStats(
            parse_counts=tuple(sorted(self._parse_counts.items())),
            resolution_counts=tuple(sorted(self._resolution_counts.items())),
        )

    def resolve(
        self,
        *,
        document: ParsedDocument,
        reference: str,
        expected: str | None = None,
        source_identity: ReferenceIdentity | None = None,
        active: tuple[ReferenceIdentity, ...] = (),
    ) -> ResolvedReference | None:
        self._cancellation.raise_if_cancelled()
        try:
            target_document, pointer = self._target(document, reference)
        except (SourceLoadError, JsonPointerError) as exc:
            code = getattr(exc, "code", "OA_REF_POINTER")
            self._diagnostics.error(
                code,
                str(exc),
                span=document.span(""),
                details=(("reference", _safe_reference(reference)),),
            )
            return None

        identity = ReferenceIdentity(target_document.source.canonical_id, pointer)
        cycle = identity in active
        if source_identity is not None and self._graph.add(source_identity, identity):
            cycle = True
        if cycle:
            self._diagnostics.warning(
                "OA_REF_CYCLE",
                f"reference cycle detected at {pointer or '#'}",
                span=target_document.span(pointer),
                details=(("reference", _safe_reference(reference)),),
            )

        cached = self._cache.get(identity)
        if cached is not None:
            if expected is not None and not _compatible(cached.value, expected):
                self._incompatible(expected, cached)
                return None
            return ResolvedReference(
                identity=cached.identity,
                document=cached.document,
                value=cached.value,
                original=reference,
                cycle=cycle or cached.cycle,
            )

        if len(active) >= self._options.max_reference_depth:
            self._diagnostics.error(
                "OA_LIMIT_REFERENCE_DEPTH",
                f"reference depth exceeds maxReferenceDepth ({self._options.max_reference_depth})",
                span=document.span(""),
            )
            return None

        try:
            value = resolve_pointer(target_document.value, pointer)
        except JsonPointerError as exc:
            self._diagnostics.error(
                "OA_REF_MISSING_TARGET",
                str(exc),
                span=target_document.span(pointer),
                details=(("reference", _safe_reference(reference)),),
            )
            return None
        resolved = ResolvedReference(identity, target_document, value, reference, cycle)
        self._cache[identity] = resolved
        self._resolution_counts[identity.value] = 1
        if self._instrumentation is not None:
            self._instrumentation("resolve", identity.value)
        if expected is not None and not _compatible(value, expected):
            self._incompatible(expected, resolved)
            return None
        return resolved

    def _target(
        self,
        document: ParsedDocument,
        reference: str,
    ) -> tuple[ParsedDocument, str]:
        split = urlsplit(reference)
        pointer = normalize_fragment(split.fragment)
        document_part = urlunsplit((split.scheme, split.netloc, split.path, split.query, ""))
        if not document_part:
            return document, pointer

        loaded = self._loader.load_reference(
            root=document.source,
            reference=document_part,
            options=self._options,
            cancellation=self._cancellation,
        )
        parsed = self._documents.get(loaded.canonical_id)
        if parsed is None:
            if len(self._documents) >= self._options.max_documents:
                raise SourceLoadError(
                    "OA_LIMIT_DOCUMENTS",
                    f"reference graph exceeds maxDocuments ({self._options.max_documents})",
                )
            parsed = self._parser.parse(
                loaded,
                self._diagnostics,
                require_openapi=False,
                options=self._options,
            )
            if parsed is None:
                raise SourceLoadError("OA_REF_PARSE_FAILED", "referenced document is invalid")
            self._documents[loaded.canonical_id] = parsed
            self._parse_counts[loaded.canonical_id] = 1
            if self._instrumentation is not None:
                self._instrumentation("parse", loaded.logical_id)
        return parsed, pointer

    def _incompatible(self, expected: str, resolved: ResolvedReference) -> None:
        self._diagnostics.error(
            "OA_REF_INCOMPATIBLE_TARGET",
            f"reference target is not a valid {expected}",
            span=resolved.document.span(resolved.identity.pointer),
            details=(("expected", expected), ("reference", _safe_reference(resolved.original))),
        )


def _compatible(value: object, expected: str) -> bool:
    if expected in {
        "schema",
        "parameter",
        "requestBody",
        "response",
        "securityScheme",
        "mapping",
    }:
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    return True


def _safe_reference(value: str) -> str:
    split = urlsplit(value)
    if split.scheme and split.netloc:
        host = split.hostname or "redacted"
        netloc = host + (f":{split.port}" if split.port else "")
        return urlunsplit((split.scheme, netloc, split.path, "", split.fragment))
    return value
