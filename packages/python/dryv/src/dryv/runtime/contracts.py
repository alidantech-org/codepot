from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath

from dryv.features.planning import GenerationPlan


class RuntimeStatus(StrEnum):
    PLAN_COMPLETE = "plan_complete"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class RuntimeResource:
    resource_id: str
    media_type: str
    content: bytes
    content_hash: str | None = None

    def __post_init__(self) -> None:
        if not self.resource_id.startswith("resource://"):
            raise ValueError("runtime resource ids must use resource://")
        if not self.media_type or self.media_type.strip() != self.media_type:
            raise ValueError("runtime resource media type must be non-empty and trimmed")


@dataclass(frozen=True, slots=True)
class RuntimePackResource:
    relative_path: str
    resource_id: str

    def __post_init__(self) -> None:
        if not self.relative_path or self.relative_path.startswith("/") or "\\" in self.relative_path:
            raise ValueError("pack bundle paths must be POSIX-relative")
        if any(part in {"", ".", ".."} for part in PurePosixPath(self.relative_path).parts):
            raise ValueError("pack bundle paths cannot contain dot or traversal segments")
        if not self.resource_id.startswith("resource://"):
            raise ValueError("pack bundle resource ids must use resource://")


@dataclass(frozen=True, slots=True)
class RuntimePack:
    instance_name: str
    manifest_resource_id: str
    resources: tuple[RuntimePackResource, ...]

    def __post_init__(self) -> None:
        if not self.instance_name or self.instance_name.strip() != self.instance_name:
            raise ValueError("runtime pack instance name must be non-empty and trimmed")
        if not self.manifest_resource_id.startswith("resource://"):
            raise ValueError("runtime pack manifest must use resource://")
        paths = tuple(item.relative_path for item in self.resources)
        if len(paths) != len(set(paths)):
            raise ValueError("pack bundle relative paths must be unique")

    def resource_id(self, relative_path: str) -> str | None:
        item = next((item for item in self.resources if item.relative_path == relative_path), None)
        return None if item is None else item.resource_id


@dataclass(frozen=True, slots=True)
class RuntimeInput:
    build_id: str
    project_resource_id: str
    canonical_ir_resource_id: str
    resources: tuple[RuntimeResource, ...]
    packs: tuple[RuntimePack, ...] = ()

    def __post_init__(self) -> None:
        if not self.build_id or self.build_id.strip() != self.build_id:
            raise ValueError("build id must be non-empty and trimmed")
        ids = tuple(item.resource_id for item in self.resources)
        if len(ids) != len(set(ids)):
            raise ValueError("runtime resource ids must be unique")
        available = set(ids)
        for required in (self.project_resource_id, self.canonical_ir_resource_id):
            if required not in available:
                raise ValueError(f"required runtime resource {required!r} is missing")
        pack_names = tuple(item.instance_name for item in self.packs)
        if len(pack_names) != len(set(pack_names)):
            raise ValueError("runtime pack instance names must be unique")
        for pack in self.packs:
            if pack.manifest_resource_id not in available:
                raise ValueError(f"pack manifest resource {pack.manifest_resource_id!r} is missing")
            for item in pack.resources:
                if item.resource_id not in available:
                    raise ValueError(f"pack resource {item.resource_id!r} is missing")


@dataclass(frozen=True, slots=True)
class RuntimeDiagnostic:
    code: str
    message: str
    level: str = "error"
    subject: str | None = None
    details: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class RuntimeTrace:
    stage: str
    message: str
    subject: str | None = None
    details: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class RuntimeResult:
    build_id: str
    status: RuntimeStatus
    plan: GenerationPlan | None
    diagnostics: tuple[RuntimeDiagnostic, ...] = ()
    trace: tuple[RuntimeTrace, ...] = ()

    @property
    def success(self) -> bool:
        return self.status is RuntimeStatus.PLAN_COMPLETE and self.plan is not None


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    core_version: str
    features: tuple[str, ...]


__all__ = [
    "RuntimeDiagnostic",
    "RuntimeInput",
    "RuntimePack",
    "RuntimePackResource",
    "RuntimeResource",
    "RuntimeResult",
    "RuntimeSnapshot",
    "RuntimeStatus",
    "RuntimeTrace",
]
