from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping, TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]

PLAN_VERSION = 2
CONTEXT_VERSION = 1
CONTEXT_CONTRACT_VERSION = 1


class PlanningError(ValueError):
    def __init__(self, code: str, message: str, *, subject: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.subject = subject


@dataclass(frozen=True, slots=True)
class PlanningName:
    name: str
    singular: str
    plural: str
    snake: str
    kebab: str
    camel: str
    pascal: str


@dataclass(frozen=True, slots=True)
class PlanningSubject:
    id: str
    kind: str
    name: PlanningName
    value: JsonObject
    semantic_dependencies: tuple[str, ...] = ()
    effective: JsonObject | None = None


@dataclass(frozen=True, slots=True)
class PlanningSelection:
    key: str
    kind: str
    bindings: tuple[str, ...] = ()
    symbols: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PlanningTemplate:
    key: str
    selection: str
    resource_id: str
    relative_path: str
    media_type: str
    content_hash: str
    renderer: str
    output_pattern: str
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PlanningPack:
    instance_name: str
    pack_id: str
    version: str
    output_root: str
    manifest_hash: str
    options: JsonObject
    bindings: JsonObject
    selections: tuple[PlanningSelection, ...]
    templates: tuple[PlanningTemplate, ...]


@dataclass(frozen=True, slots=True)
class PlanningInput:
    build_id: str
    project_name: str
    ir_hash: str
    subjects: tuple[PlanningSubject, ...]
    packs: tuple[PlanningPack, ...]


@dataclass(frozen=True, slots=True)
class RendererRequirement:
    capability: str


@dataclass(frozen=True, slots=True)
class TemplateReference:
    pack_id: str
    pack_instance: str
    template_key: str
    resource_id: str
    relative_path: str
    media_type: str
    content_hash: str


@dataclass(frozen=True, slots=True)
class ContextContract:
    version: int
    paths: tuple[str, ...]
    hash: str


@dataclass(frozen=True, slots=True)
class PlannedArtifact:
    id: str
    path: str
    job_id: str
    semantic_ids: tuple[str, ...]
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PlanDependency:
    job_id: str
    depends_on_job_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class RenderJob:
    id: str
    order: int
    subject_id: str
    subject_kind: str
    pack_id: str
    pack_instance: str
    selection_key: str
    selection_reason: str
    renderer: RendererRequirement
    template: TemplateReference
    context: JsonObject
    context_contract: ContextContract
    context_hash: str
    artifact: PlannedArtifact
    dependencies: tuple[str, ...]
    semantic_dependencies: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    version: int
    context_version: int
    build_id: str
    project_name: str
    ir_hash: str
    pack_hashes: tuple[tuple[str, str], ...]
    required_renderers: tuple[RendererRequirement, ...]
    jobs: tuple[RenderJob, ...]
    artifacts: tuple[PlannedArtifact, ...]
    dependencies: tuple[PlanDependency, ...]
    plan_hash: str

    def canonical_document(self, *, include_hash: bool = True) -> JsonObject:
        document: JsonObject = {
            "version": self.version,
            "contextVersion": self.context_version,
            "buildId": self.build_id,
            "projectName": self.project_name,
            "irHash": self.ir_hash,
            "packHashes": [[name, digest] for name, digest in self.pack_hashes],
            "requiredRenderers": [item.capability for item in self.required_renderers],
            "jobs": [_job_document(item) for item in self.jobs],
            "artifacts": [_artifact_document(item) for item in self.artifacts],
            "dependencies": [
                {
                    "jobId": item.job_id,
                    "dependsOnJobId": item.depends_on_job_id,
                    "reason": item.reason,
                }
                for item in self.dependencies
            ],
        }
        if include_hash:
            document["planHash"] = self.plan_hash
        return document

    def canonical_bytes(self) -> bytes:
        return json.dumps(
            self.canonical_document(),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")


def _job_document(job: RenderJob) -> JsonObject:
    return {
        "id": job.id,
        "order": job.order,
        "subjectId": job.subject_id,
        "subjectKind": job.subject_kind,
        "packId": job.pack_id,
        "packInstance": job.pack_instance,
        "selectionKey": job.selection_key,
        "selectionReason": job.selection_reason,
        "renderer": job.renderer.capability,
        "template": {
            "packId": job.template.pack_id,
            "packInstance": job.template.pack_instance,
            "templateKey": job.template.template_key,
            "resourceId": job.template.resource_id,
            "relativePath": job.template.relative_path,
            "mediaType": job.template.media_type,
            "contentHash": job.template.content_hash,
        },
        "context": job.context,
        "contextHash": job.context_hash,
        "contextContract": {
            "version": job.context_contract.version,
            "paths": list(job.context_contract.paths),
            "hash": job.context_contract.hash,
        },
        "artifactId": job.artifact.id,
        "dependencies": list(job.dependencies),
        "semanticDependencies": list(job.semantic_dependencies),
    }


def _artifact_document(artifact: PlannedArtifact) -> JsonObject:
    return {
        "id": artifact.id,
        "path": artifact.path,
        "jobId": artifact.job_id,
        "semanticIds": list(artifact.semantic_ids),
        "dependencies": list(artifact.dependencies),
    }


__all__ = [
    "CONTEXT_CONTRACT_VERSION",
    "CONTEXT_VERSION",
    "ContextContract",
    "GenerationPlan",
    "JsonObject",
    "JsonValue",
    "PLAN_VERSION",
    "PlanDependency",
    "PlannedArtifact",
    "PlanningError",
    "PlanningInput",
    "PlanningName",
    "PlanningPack",
    "PlanningSelection",
    "PlanningSubject",
    "PlanningTemplate",
    "RenderJob",
    "RendererRequirement",
    "TemplateReference",
]
