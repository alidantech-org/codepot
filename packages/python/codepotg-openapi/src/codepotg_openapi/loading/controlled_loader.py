from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable
from urllib.parse import urljoin, urlsplit

from codepotg.api import CancellationToken
from codepotg.diagnostics import SourceIdentity, SourceKind
from codepotg.ports import SourceAdapterRequest

from ..options import ExternalReferencePolicy, OpenApiOptions
from .policy import SourcePolicy
from .source import LoadedSource


class SourceLoadError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@runtime_checkable
class ReferenceLoader(Protocol):
    @property
    def authority_id(self) -> str: ...

    def load(self, identity: str, cancellation: CancellationToken) -> str | bytes: ...


@dataclass(frozen=True, slots=True)
class CallableReferenceLoader:
    callback: Callable[[str, CancellationToken], str | bytes]
    authority_id: str = "host-controlled"

    def load(self, identity: str, cancellation: CancellationToken) -> str | bytes:
        return self.callback(identity, cancellation)


@dataclass(slots=True)
class SourceLoadingSession:
    """One normalization call's source cache.

    The authority object is reusable, but referenced bytes never outlive this
    session. A new adapter normalization creates a new session.
    """

    loader: ControlledSourceLoader
    _reference_cache: dict[str, LoadedSource] = field(default_factory=dict)

    @property
    def authority_id(self) -> str:
        return self.loader.authority_id

    def load_root(
        self,
        request: SourceAdapterRequest,
        options: OpenApiOptions,
        cancellation: CancellationToken,
    ) -> LoadedSource:
        return self.loader.load_root(request, options, cancellation)

    def load_reference(
        self,
        *,
        root: LoadedSource,
        reference: str,
        options: OpenApiOptions,
        cancellation: CancellationToken,
    ) -> LoadedSource:
        key = self.loader.reference_key(root, reference)
        cached = self._reference_cache.get(key)
        if cached is not None:
            return cached
        loaded = self.loader.load_reference(
            root=root,
            reference=reference,
            options=options,
            cancellation=cancellation,
        )
        self._reference_cache[key] = loaded
        return loaded


class ControlledSourceLoader:
    """Reusable host authority with no cross-normalization mutable state."""

    def __init__(
        self,
        *,
        source_policy: SourcePolicy,
        reference_loader: ReferenceLoader | None,
    ) -> None:
        self._source_policy = source_policy
        self._reference_loader = reference_loader

    @property
    def authority_id(self) -> str:
        if self._reference_loader is None:
            return "local-contained"
        return f"controlled:{self._reference_loader.authority_id}"

    def new_session(self) -> SourceLoadingSession:
        return SourceLoadingSession(self)

    def load_root(
        self,
        request: SourceAdapterRequest,
        options: OpenApiOptions,
        cancellation: CancellationToken,
    ) -> LoadedSource:
        cancellation.raise_if_cancelled()
        if request.content is not None:
            if not self._source_policy.allow_memory:
                raise SourceLoadError("OA_SOURCE_MEMORY_DENIED", "in-memory sources are denied")
            content = _to_bytes(request.content)
            _check_size(content, options.max_source_bytes)
            return LoadedSource(
                identity=SourceIdentity(SourceKind.MEMORY, _redact(request.source_id)),
                canonical_id=f"memory:{request.source_id}",
                logical_id=f"memory:{request.source_id}",
                content=content,
            )

        assert request.location is not None
        location = request.location
        scheme = _uri_scheme(location)
        if scheme:
            raise SourceLoadError(
                "OA_SOURCE_SCHEME_DENIED",
                f"source URI scheme {scheme!r} is not supported",
            )
        path = Path(location).expanduser()
        if not path.is_absolute():
            raise SourceLoadError(
                "OA_SOURCE_RELATIVE_PATH",
                "local source locations must be absolute",
            )
        try:
            canonical = path.resolve(strict=True)
        except OSError as exc:
            raise SourceLoadError("OA_SOURCE_NOT_FOUND", "local source could not be read") from exc
        if not canonical.is_file():
            raise SourceLoadError("OA_SOURCE_NOT_FILE", "local source is not a regular file")

        configured_root = self._source_policy.canonical_root()
        authorized_root = configured_root or canonical.parent
        _require_contained(canonical, authorized_root)
        cancellation.raise_if_cancelled()
        try:
            content = canonical.read_bytes()
        except OSError as exc:
            raise SourceLoadError(
                "OA_SOURCE_READ_FAILED", "local source could not be read"
            ) from exc
        _check_size(content, options.max_source_bytes)
        return LoadedSource(
            identity=SourceIdentity(SourceKind.FILE, canonical.as_posix()),
            canonical_id=f"file:{canonical.as_posix()}",
            logical_id=f"file:{request.source_id}",
            content=content,
            path=canonical,
            authorized_root=authorized_root,
        )

    def reference_key(self, root: LoadedSource, reference: str) -> str:
        effective_reference = _effective_reference(root, reference)
        scheme = _uri_scheme(effective_reference)
        if scheme in {"http", "https", "ftp"}:
            return f"controlled:{effective_reference}"
        if scheme:
            return f"unsupported:{effective_reference}"
        if root.path is None or root.authorized_root is None:
            return f"controlled:{root.canonical_id}:{effective_reference}"
        split = urlsplit(effective_reference)
        candidate = (root.path.parent / split.path).resolve(strict=False)
        _require_contained(candidate, root.authorized_root)
        return f"file:{candidate.as_posix()}"

    def load_reference(
        self,
        *,
        root: LoadedSource,
        reference: str,
        options: OpenApiOptions,
        cancellation: CancellationToken,
    ) -> LoadedSource:
        cancellation.raise_if_cancelled()
        effective_reference = _effective_reference(root, reference)
        split = urlsplit(effective_reference)
        scheme = _uri_scheme(effective_reference)
        if scheme in {"http", "https", "ftp"}:
            if options.external_references is not ExternalReferencePolicy.CONTROLLED:
                raise SourceLoadError(
                    "OA_REF_NETWORK_DENIED",
                    f"external reference scheme {split.scheme!r} is denied",
                )
            if self._reference_loader is None:
                raise SourceLoadError(
                    "OA_REF_CONTROLLED_LOADER_REQUIRED",
                    "controlled external references require a host loader",
                )
            content = _to_bytes(self._reference_loader.load(effective_reference, cancellation))
            _check_size(content, options.max_source_bytes)
            safe_identity = _redact(effective_reference)
            return LoadedSource(
                identity=SourceIdentity(SourceKind.MEMORY, safe_identity),
                canonical_id=f"controlled-private:{effective_reference}",
                logical_id=f"controlled:{safe_identity}",
                content=content,
                retrieval_id=effective_reference,
            )
        if scheme:
            raise SourceLoadError(
                "OA_REF_SCHEME_DENIED",
                f"reference URI scheme {scheme!r} is not supported",
            )
        if options.external_references is ExternalReferencePolicy.DENY:
            raise SourceLoadError("OA_REF_EXTERNAL_DENIED", "external references are denied")
        if root.path is None or root.authorized_root is None:
            if options.external_references is ExternalReferencePolicy.CONTROLLED:
                if self._reference_loader is None:
                    raise SourceLoadError(
                        "OA_REF_CONTROLLED_LOADER_REQUIRED",
                        "controlled external references require a host loader",
                    )
                content = _to_bytes(self._reference_loader.load(effective_reference, cancellation))
                _check_size(content, options.max_source_bytes)
                safe_identity = _redact(effective_reference)
                return LoadedSource(
                    identity=SourceIdentity(SourceKind.MEMORY, safe_identity),
                    canonical_id=f"controlled-private:{root.canonical_id}:{effective_reference}",
                    logical_id=f"controlled:{safe_identity}",
                    content=content,
                    retrieval_id=effective_reference,
                )
            raise SourceLoadError(
                "OA_REF_LOCAL_BASE_REQUIRED",
                "memory sources require a controlled loader for external documents",
            )

        candidate = (root.path.parent / split.path).resolve(strict=False)
        _require_contained(candidate, root.authorized_root)
        try:
            canonical = candidate.resolve(strict=True)
            if not canonical.is_file():
                raise OSError("not a file")
            content = canonical.read_bytes()
        except OSError as exc:
            raise SourceLoadError(
                "OA_REF_NOT_FOUND", "referenced local document was not found"
            ) from exc
        _check_size(content, options.max_source_bytes)
        relative = canonical.relative_to(root.authorized_root).as_posix()
        return LoadedSource(
            identity=SourceIdentity(SourceKind.FILE, canonical.as_posix()),
            canonical_id=f"file:{canonical.as_posix()}",
            logical_id=f"local:{relative}",
            content=content,
            path=canonical,
            authorized_root=root.authorized_root,
        )


def _effective_reference(root: LoadedSource, reference: str) -> str:
    if root.retrieval_id and "://" in root.retrieval_id and "://" not in reference:
        return urljoin(root.retrieval_id, reference)
    return reference


def _to_bytes(value: str | bytes) -> bytes:
    return value if isinstance(value, bytes) else value.encode("utf-8")


def _check_size(content: bytes, maximum: int) -> None:
    if len(content) > maximum:
        raise SourceLoadError(
            "OA_LIMIT_SOURCE_BYTES",
            f"source exceeds maxSourceBytes ({maximum})",
        )


def _require_contained(path: Path, root: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise SourceLoadError(
            "OA_SOURCE_PATH_ESCAPE",
            "local path escapes the authorized root",
        ) from exc


def _redact(value: str) -> str:
    split = urlsplit(value)
    if split.scheme and split.netloc:
        host = split.hostname or "redacted"
        port = f":{split.port}" if split.port else ""
        return f"{split.scheme}://{host}{port}{split.path}"
    return value


def _uri_scheme(value: str) -> str:
    if re.match(r"^[A-Za-z]:[\\/]", value):
        return ""
    return urlsplit(value).scheme.lower()
