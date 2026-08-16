from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Mapping

from dryv.features.planning import GenerationPlan

BUNDLE_MANIFEST_VERSION = "dryv.bundle/v1"


@dataclass(frozen=True, slots=True)
class RenderedArtifactMetadata:
    artifact_id: str
    size: int
    content_hash: str


@dataclass(frozen=True, slots=True)
class BundleArtifactEntry:
    plan_index: int
    artifact_id: str
    path: str
    size: int
    content_hash: str
    semantic_ids: tuple[str, ...]
    subject_id: str
    subject_kind: str
    pack_id: str
    pack_instance: str
    template_key: str
    template_hash: str


@dataclass(frozen=True, slots=True)
class BundleManifest:
    version: str
    build_id: str
    plan_hash: str
    artifacts: tuple[BundleArtifactEntry, ...]

    def document(self) -> dict[str, object]:
        return {
            "version": self.version,
            "buildId": self.build_id,
            "planHash": self.plan_hash,
            "artifacts": [
                {
                    "planIndex": item.plan_index,
                    "artifactId": item.artifact_id,
                    "path": item.path,
                    "size": item.size,
                    "contentHash": item.content_hash,
                    "semanticIds": list(item.semantic_ids),
                    "subjectId": item.subject_id,
                    "subjectKind": item.subject_kind,
                    "packId": item.pack_id,
                    "packInstance": item.pack_instance,
                    "templateKey": item.template_key,
                    "templateHash": item.template_hash,
                }
                for item in self.artifacts
            ],
        }

    def bytes(self) -> bytes:
        return json.dumps(
            self.document(),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8") + b"\n"


def build_bundle_manifest(
    plan: GenerationPlan,
    rendered: Mapping[str, RenderedArtifactMetadata],
) -> BundleManifest:
    entries: list[BundleArtifactEntry] = []
    jobs = {job.artifact.id: job for job in plan.jobs}
    for artifact in plan.artifacts:
        metadata = rendered.get(artifact.id)
        job = jobs.get(artifact.id)
        if metadata is None or job is None:
            raise ValueError(f"bundle is missing rendered artifact {artifact.id!r}")
        _safe_path(artifact.path)
        entries.append(
            BundleArtifactEntry(
                job.order,
                artifact.id,
                artifact.path,
                metadata.size,
                metadata.content_hash,
                artifact.semantic_ids,
                job.subject_id,
                job.subject_kind,
                job.pack_id,
                job.pack_instance,
                job.template.template_key,
                job.template.content_hash,
            )
        )
    return BundleManifest(
        BUNDLE_MANIFEST_VERSION,
        plan.build_id,
        plan.plan_hash,
        tuple(sorted(entries, key=lambda item: (item.plan_index, item.path, item.artifact_id))),
    )


def _safe_path(value: str) -> None:
    if not value or value.startswith("/") or "\\" in value:
        raise ValueError(f"unsafe artifact path {value!r}")
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe artifact path {value!r}")


__all__ = [
    "BUNDLE_MANIFEST_VERSION",
    "BundleArtifactEntry",
    "BundleManifest",
    "RenderedArtifactMetadata",
    "build_bundle_manifest",
]
