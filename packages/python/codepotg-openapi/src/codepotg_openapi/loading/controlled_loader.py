from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
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


class ControlledSourceLoader:
    def __init__(
        self,
        *,
        source_policy: SourcePolicy,
        reference_loader: ReferenceLoader | None,
    ) -> None:
        self._source_policy = source_policy
        self._reference_loader = reference_loader
        self._reference_cache: dict[str, LoadedSource] = {}

    @property
    def authority_id(self) -> str:
        if self._reference_loader is None:
            return "local-contained"
        return f"controlled:{self._reference_loader.authority_id}"

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
            raise SourceLoadError("OA_SOURCE_READ_FAILED", "local source could not be read") from exc
        _check_size(content, options.max_source_bytes)
        logical = f"file:{request.source_id}"
        return LoadedSource(
            identity=SourceIdentity(SourceKind.FILE, canonical.as_posix()),
            canonical_id=f"file:{canonical.as_posix()}",
            logical_id=logical,
            content=content,
            path=canonical,
            authorized_root=authorized_root,
        )

    def load_reference(
        self,
        *,
        root: LoadedSource,
        reference: str,
        options: OpenApiOptions,
        cancellation: CancellationToken,
    ) -> LoadedSource:
        cancellation.raise_if_cancelled()
        effective_reference = reference
        if root.retrieval_id and "://" in root.retrieval_id and "://" not in reference:
            effective_reference = urljoin(root.retrieval_id, reference)
        split = urlsplit(effective_reference)
        scheme = _uri_scheme(effective_reference)
        if scheme in {"http", "https", "ftp"}:
            cache_key = f"controlled:{effective_reference}"
            cached = self._reference_cache.get(cache_key)
            if cached is not None:
                return cached
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
            loaded = LoadedSource(
                identity=SourceIdentity(SourceKind.MEMORY, safe_identity),
                canonical_id=f"controlled-private:{effective_reference}",
                logical_id=f"controlled:{safe_identity}",
                content=content,
                retrieval_id=effective_reference,
            )
            self._reference_cache[cache_key] = loaded
            return loaded
        if scheme:
            raise SourceLoadError(
                "OA_REF_SCHEME_DENIED",
                f"reference URI scheme {scheme!r} is not supported",
            )
        if options.external_references is ExternalReferencePolicy.DENY:
            raise SourceLoadError("OA_REF_EXTERNAL_DENIED", "external references are denied")
        if root.path is None or root.authorized_root is None:
            if options.external_references is ExternalReferencePolicy.CONTROLLED:
                cache_key = f"controlled:{root.canonical_id}:{effective_reference}"
                cached = self._reference_cache.get(cache_key)
                if cached is not None:
                    return cached
                if self._reference_loader is None:
                    raise SourceLoadError(
                        "OA_REF_CONTROLLED_LOADER_REQUIRED",
                        "controlled external references require a host loader",
                    )
                content = _to_bytes(self._reference_loader.load(effective_reference, cancellation))
                _check_size(content, options.max_source_bytes)
                safe_identity = _redact(effective_reference)
                loaded = LoadedSource(
                    identity=SourceIdentity(SourceKind.MEMORY, safe_identity),
                    canonical_id=f"controlled-private:{effective_reference}",
                    logical_id=f"controlled:{safe_identity}",
                    content=content,
                    retrieval_id=effective_reference,
                )
                self._reference_cache[cache_key] = loaded
                return loaded
            raise SourceLoadError(
                "OA_REF_LOCAL_BASE_REQUIRED",
                "memory sources require a controlled loader for external documents",
            )

        candidate = (root.path.parent / split.path).resolve(strict=False)
        _require_contained(candidate, root.authorized_root)
        cache_key = f"file:{candidate.as_posix()}"
        cached = self._reference_cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            canonical = candidate.resolve(strict=True)
            if not canonical.is_file():
                raise OSError("not a file")
            content = canonical.read_bytes()
        except OSError as exc:
            raise SourceLoadError("OA_REF_NOT_FOUND", "referenced local document was not found") from exc
        _check_size(content, options.max_source_bytes)
        relative = canonical.relative_to(root.authorized_root).as_posix()
        loaded = LoadedSource(
            identity=SourceIdentity(SourceKind.FILE, canonical.as_posix()),
            canonical_id=f"file:{canonical.as_posix()}",
            logical_id=f"local:{relative}",
            content=content,
            path=canonical,
            authorized_root=root.authorized_root,
        )
        self._reference_cache[cache_key] = loaded
        return loaded


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
