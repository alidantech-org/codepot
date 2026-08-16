from __future__ import annotations

from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import BinaryIO


class ArtifactVerificationError(ValueError):
    def __init__(self, code: str, message: str, *, artifact_id: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.artifact_id = artifact_id


def safe_artifact_path(value: str) -> PurePosixPath:
    if not value or value.startswith("/") or "\\" in value:
        raise ArtifactVerificationError("CLI_ARTIFACT_PATH", f"unsafe artifact path {value!r}")
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ArtifactVerificationError("CLI_ARTIFACT_PATH", f"unsafe artifact path {value!r}")
    first = path.parts[0]
    if len(first) >= 2 and first[1] == ":":
        raise ArtifactVerificationError(
            "CLI_ARTIFACT_PATH", f"drive-qualified artifact path {value!r} is forbidden"
        )
    if first == ".dryv":
        raise ArtifactVerificationError(
            "CLI_ARTIFACT_RESERVED",
            f"artifact path {value!r} uses the Project Client reserved .dryv namespace",
        )
    return path


def content_hash_stream(stream: BinaryIO, *, reset: bool = True) -> tuple[int, str]:
    original = stream.tell() if reset else None
    stream.seek(0)
    digest = sha256()
    size = 0
    while True:
        chunk = stream.read(64 * 1024)
        if not chunk:
            break
        digest.update(chunk)
        size += len(chunk)
    if original is not None:
        stream.seek(original)
    return size, f"sha256:{digest.hexdigest()}"


def verify_file(path: Path, *, size: int, content_hash: str, artifact_id: str) -> None:
    digest = sha256()
    actual_size = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(64 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            actual_size += len(chunk)
    actual_hash = f"sha256:{digest.hexdigest()}"
    if actual_size != size:
        raise ArtifactVerificationError(
            "CLI_ARTIFACT_SIZE",
            f"artifact {artifact_id!r} expected {size} bytes but received {actual_size}",
            artifact_id=artifact_id,
        )
    if actual_hash != content_hash:
        raise ArtifactVerificationError(
            "CLI_ARTIFACT_HASH",
            f"artifact {artifact_id!r} content hash does not match received bytes",
            artifact_id=artifact_id,
        )


__all__ = [
    "ArtifactVerificationError",
    "content_hash_stream",
    "safe_artifact_path",
    "verify_file",
]
