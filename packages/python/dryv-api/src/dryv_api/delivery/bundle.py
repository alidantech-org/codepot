from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from tempfile import SpooledTemporaryFile
from threading import Event, Lock, Thread
from typing import BinaryIO, Iterator
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from dryv_api.builds import BuildEventType, BuildSession
from dryv_api.contracts import ApiContractError, BuildDiagnostic

from .manifest import BundleManifest, RenderedArtifactMetadata, build_bundle_manifest
from .streaming import ArtifactData, ArtifactFinished, ArtifactStarted, ArtifactStream

_ARTIFACT_MEMORY_LIMIT = 4 * 1024 * 1024
_BUNDLE_MEMORY_LIMIT = 8 * 1024 * 1024
_COPY_CHUNK = 64 * 1024
_FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


@dataclass(frozen=True, slots=True)
class BundleMetadata:
    build_id: str
    size: int
    content_hash: str
    artifact_count: int


class BundleHandle:
    """Thread-safe handle to one deterministic generated-output ZIP."""

    def __init__(self, build_id: str) -> None:
        self.build_id = build_id
        self.ready = Event()
        self._lock = Lock()
        self._file: BinaryIO | None = None
        self._metadata: BundleMetadata | None = None
        self._manifest: BundleManifest | None = None
        self._error: Exception | None = None

    @property
    def metadata(self) -> BundleMetadata | None:
        with self._lock:
            return self._metadata

    @property
    def manifest(self) -> BundleManifest | None:
        with self._lock:
            return self._manifest

    @property
    def error(self) -> Exception | None:
        with self._lock:
            return self._error

    def wait(self, timeout: float | None = None) -> bool:
        return self.ready.wait(timeout)

    def chunks(self, *, chunk_size: int = _COPY_CHUNK) -> Iterator[bytes]:
        if chunk_size < 1:
            raise ValueError("bundle chunk_size must be positive")
        if not self.ready.is_set():
            raise ApiContractError("API_BUNDLE_NOT_READY", f"bundle {self.build_id!r} is not ready")
        with self._lock:
            if self._error is not None:
                raise ApiContractError("API_BUNDLE_FAILED", str(self._error))
            if self._file is None:
                raise ApiContractError("API_BUNDLE_MISSING", f"bundle {self.build_id!r} has no content")
            self._file.seek(0)
            while True:
                chunk = self._file.read(chunk_size)
                if not chunk:
                    return
                yield chunk

    def complete(
        self,
        file: BinaryIO,
        metadata: BundleMetadata,
        manifest: BundleManifest,
    ) -> None:
        with self._lock:
            self._file = file
            self._metadata = metadata
            self._manifest = manifest
        self.ready.set()

    def fail(self, error: Exception) -> None:
        with self._lock:
            self._error = error
        self.ready.set()

    def close(self) -> None:
        with self._lock:
            file = self._file
            self._file = None
        if file is not None:
            file.close()


class BundleBuilder:
    """Consume an ArtifactStream and package it deterministically without unbounded RAM."""

    def __init__(self) -> None:
        self._handles: dict[str, BundleHandle] = {}
        self._lock = Lock()

    def start(self, session: BuildSession, stream: ArtifactStream) -> BundleHandle:
        if session.plan is None:
            raise ApiContractError("API_PLAN_NOT_READY", "bundle build requires a GenerationPlan")
        handle = BundleHandle(session.build_id)
        with self._lock:
            if session.build_id in self._handles:
                raise ApiContractError("API_BUNDLE_EXISTS", f"bundle for build {session.build_id!r} already exists")
            self._handles[session.build_id] = handle
        Thread(
            target=self._build,
            args=(session, stream, handle),
            name=f"dryv-bundle-{session.build_id}",
            daemon=True,
        ).start()
        return handle

    def get(self, build_id: str) -> BundleHandle | None:
        with self._lock:
            return self._handles.get(build_id)

    def require(self, build_id: str) -> BundleHandle:
        handle = self.get(build_id)
        if handle is None:
            raise ApiContractError("API_BUNDLE_MISSING", f"build {build_id!r} has no bundle")
        return handle

    def release(self, build_id: str) -> bool:
        with self._lock:
            handle = self._handles.pop(build_id, None)
        if handle is None:
            return False
        handle.close()
        return True

    def _build(self, session: BuildSession, stream: ArtifactStream, handle: BundleHandle) -> None:
        files: dict[str, BinaryIO] = {}
        paths: dict[str, str] = {}
        metadata: dict[str, RenderedArtifactMetadata] = {}
        completed = 0
        plan = session.plan
        assert plan is not None
        session.emit(BuildEventType.BUNDLE_STARTED, "Bundle packaging started")
        try:
            for event in stream:
                if isinstance(event, ArtifactStarted):
                    if event.artifact_id in files:
                        raise ApiContractError("API_BUNDLE_ARTIFACT_DUPLICATE", f"artifact {event.artifact_id!r} started twice")
                    files[event.artifact_id] = SpooledTemporaryFile(max_size=_ARTIFACT_MEMORY_LIMIT, mode="w+b")
                    paths[event.artifact_id] = event.path
                elif isinstance(event, ArtifactData):
                    file = files.get(event.artifact_id)
                    if file is None or file.tell() != event.offset:
                        raise ApiContractError("API_BUNDLE_OFFSET", f"invalid bundle offset for {event.artifact_id!r}")
                    file.write(event.content)
                elif isinstance(event, ArtifactFinished):
                    file = files.get(event.artifact_id)
                    if file is None:
                        raise ApiContractError("API_BUNDLE_ARTIFACT_MISSING", f"artifact {event.artifact_id!r} was never started")
                    if file.tell() != event.size:
                        raise ApiContractError("API_BUNDLE_SIZE", f"artifact {event.artifact_id!r} size changed during bundling")
                    actual_hash = _file_hash(file)
                    if actual_hash != event.content_hash:
                        raise ApiContractError("API_BUNDLE_HASH", f"artifact {event.artifact_id!r} hash changed during bundling")
                    metadata[event.artifact_id] = RenderedArtifactMetadata(event.artifact_id, event.size, event.content_hash)
                    completed += 1
                    session.emit(
                        BuildEventType.BUNDLE_PROGRESS,
                        "Bundle artifact collected",
                        subject=event.artifact_id,
                        details=(("completed", str(completed)), ("total", str(len(plan.artifacts)))),
                    )

            if session.status.value != "render_complete":
                raise ApiContractError("API_BUNDLE_RENDER_INCOMPLETE", "rendering did not complete successfully")
            manifest = build_bundle_manifest(plan, metadata)
            bundle_file = SpooledTemporaryFile(max_size=_BUNDLE_MEMORY_LIMIT, mode="w+b")
            with ZipFile(bundle_file, mode="w", compression=ZIP_STORED, allowZip64=True) as archive:
                _write_bytes(archive, ".dryv/manifest.json", manifest.bytes())
                for entry in manifest.artifacts:
                    file = files[entry.artifact_id]
                    file.seek(0)
                    _write_file(archive, entry.path, file)
            bundle_file.seek(0)
            size = _file_size(bundle_file)
            content_hash = _file_hash(bundle_file)
            bundle_file.seek(0)
            bundle_metadata = BundleMetadata(session.build_id, size, content_hash, len(manifest.artifacts))
            handle.complete(bundle_file, bundle_metadata, manifest)
            session.emit(
                BuildEventType.BUNDLE_READY,
                "Deterministic ZIP bundle is ready",
                details=(
                    ("size", str(size)),
                    ("contentHash", content_hash),
                    ("artifacts", str(len(manifest.artifacts))),
                ),
            )
        except Exception as exc:
            handle.fail(exc)
            if not session.cancelled:
                code = getattr(exc, "code", "API_BUNDLE_FAILED")
                message = getattr(exc, "message", str(exc))
                session.fail((BuildDiagnostic(str(code), str(message)),))
        finally:
            for file in files.values():
                file.close()


def _zip_info(path: str) -> ZipInfo:
    info = ZipInfo(path, date_time=_FIXED_ZIP_TIME)
    info.compress_type = ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def _write_bytes(archive: ZipFile, path: str, content: bytes) -> None:
    with archive.open(_zip_info(path), mode="w", force_zip64=True) as target:
        target.write(content)


def _write_file(archive: ZipFile, path: str, source: BinaryIO) -> None:
    with archive.open(_zip_info(path), mode="w", force_zip64=True) as target:
        while True:
            chunk = source.read(_COPY_CHUNK)
            if not chunk:
                return
            target.write(chunk)


def _file_hash(file: BinaryIO) -> str:
    position = file.tell()
    file.seek(0)
    digest = sha256()
    while True:
        chunk = file.read(_COPY_CHUNK)
        if not chunk:
            break
        digest.update(chunk)
    file.seek(position)
    return f"sha256:{digest.hexdigest()}"


def _file_size(file: BinaryIO) -> int:
    position = file.tell()
    file.seek(0, 2)
    size = file.tell()
    file.seek(position)
    return size


__all__ = ["BundleBuilder", "BundleHandle", "BundleMetadata"]
