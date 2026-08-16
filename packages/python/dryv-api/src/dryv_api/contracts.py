from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath

API_VERSION = "dryv.api/v1"


class ApiContractError(ValueError):
    def __init__(self, code: str, message: str, *, path: str = "$") -> None:
        super().__init__(f"{path}: {message}")
        self.code = code
        self.message = message
        self.path = path


class BuildStatus(StrEnum):
    ACCEPTED = "accepted"
    PLANNING = "planning"
    PLAN_READY = "plan_ready"
    PREFLIGHT = "preflight"
    RENDER_READY = "render_ready"
    RENDERING = "rendering"
    RENDER_COMPLETE = "render_complete"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class BuildResourceUpload:
    resource_id: str
    media_type: str
    content: bytes
    content_hash: str | None = None

    def __post_init__(self) -> None:
        if not self.resource_id.startswith("resource://") or self.resource_id.strip() != self.resource_id:
            raise ApiContractError("API_RESOURCE_ID", "resource id must use resource://")
        if not self.media_type or self.media_type.strip() != self.media_type:
            raise ApiContractError("API_MEDIA_TYPE", "media type must be non-empty and trimmed")


@dataclass(frozen=True, slots=True)
class PackResourceUpload:
    relative_path: str
    resource: BuildResourceUpload

    def __post_init__(self) -> None:
        if not self.relative_path or self.relative_path.startswith("/") or "\\" in self.relative_path:
            raise ApiContractError("API_PACK_PATH", "pack resource path must be POSIX-relative")
        path = PurePosixPath(self.relative_path)
        if any(part in {"", ".", ".."} for part in path.parts):
            raise ApiContractError("API_PACK_PATH", "pack resource path contains an invalid segment")


@dataclass(frozen=True, slots=True)
class PackBundleUpload:
    instance_name: str
    manifest: BuildResourceUpload
    resources: tuple[PackResourceUpload, ...] = ()

    def __post_init__(self) -> None:
        if not self.instance_name or self.instance_name.strip() != self.instance_name or any(character.isspace() for character in self.instance_name):
            raise ApiContractError("API_PACK_INSTANCE", "pack instance name must be a non-empty identifier")
        paths = tuple(item.relative_path for item in self.resources)
        if len(paths) != len(set(paths)):
            raise ApiContractError("API_PACK_PATH_DUPLICATE", "pack bundle paths must be unique")


@dataclass(frozen=True, slots=True)
class CreateBuildRequest:
    build_id: str
    project: BuildResourceUpload
    canonical_ir: BuildResourceUpload
    packs: tuple[PackBundleUpload, ...] = ()
    resources: tuple[BuildResourceUpload, ...] = ()

    def __post_init__(self) -> None:
        if not self.build_id or self.build_id.strip() != self.build_id:
            raise ApiContractError("API_BUILD_ID", "build id must be non-empty and trimmed")
        names = tuple(item.instance_name for item in self.packs)
        if len(names) != len(set(names)):
            raise ApiContractError("API_PACK_DUPLICATE", "pack instance names must be unique")


@dataclass(frozen=True, slots=True)
class BuildDiagnostic:
    code: str
    message: str
    level: str = "error"
    subject: str | None = None
    details: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class BuildSummary:
    build_id: str
    status: BuildStatus
    plan_hash: str | None = None
    job_count: int = 0
    artifact_count: int = 0
    diagnostics: tuple[BuildDiagnostic, ...] = ()


__all__ = [
    "API_VERSION",
    "ApiContractError",
    "BuildDiagnostic",
    "BuildResourceUpload",
    "BuildStatus",
    "BuildSummary",
    "CreateBuildRequest",
    "PackBundleUpload",
    "PackResourceUpload",
]
