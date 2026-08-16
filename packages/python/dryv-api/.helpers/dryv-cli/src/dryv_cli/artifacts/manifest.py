from __future__ import annotations

from dataclasses import dataclass

from .model import ArtifactProvenance
from .verify import ArtifactVerificationError, safe_artifact_path


@dataclass(frozen=True, slots=True)
class PlannedArtifactMetadata:
    artifact_id: str
    path: str
    provenance: ArtifactProvenance


def planned_artifacts(plan: dict[str, object]) -> dict[str, PlannedArtifactMetadata]:
    artifacts_raw = plan.get("artifacts")
    jobs_raw = plan.get("jobs")
    if not isinstance(artifacts_raw, list) or not isinstance(jobs_raw, list):
        raise ArtifactVerificationError(
            "CLI_PLAN_ARTIFACTS",
            "GenerationPlan requires artifacts and jobs arrays",
        )

    job_order: dict[str, int] = {}
    order_ids: set[int] = set()
    job_subject: dict[
        str,
        tuple[str | None, str | None, str | None, str | None, str | None, str | None],
    ] = {}
    for raw in jobs_raw:
        if not isinstance(raw, dict):
            raise ArtifactVerificationError(
                "CLI_PLAN_JOB",
                "GenerationPlan job must be an object",
            )
        job_id = _string(raw.get("id"), "job.id")
        if job_id in job_order:
            raise ArtifactVerificationError(
                "CLI_PLAN_JOB_DUPLICATE",
                f"GenerationPlan contains duplicate job id {job_id!r}",
            )
        order = raw.get("order")
        if (
            not isinstance(order, int)
            or isinstance(order, bool)
            or order < 0
        ):
            raise ArtifactVerificationError(
                "CLI_PLAN_JOB",
                "GenerationPlan job order must be a non-negative integer",
            )
        if order in order_ids:
            raise ArtifactVerificationError(
                "CLI_PLAN_JOB_DUPLICATE",
                f"GenerationPlan contains duplicate job order {order}",
            )
        template = raw.get("template")
        if not isinstance(template, dict):
            raise ArtifactVerificationError(
                "CLI_PLAN_JOB",
                "GenerationPlan job template must be an object",
            )
        job_order[job_id] = order
        order_ids.add(order)
        job_subject[job_id] = (
            _optional_string(raw.get("subjectId")),
            _optional_string(raw.get("subjectKind")),
            _optional_string(raw.get("packId")),
            _optional_string(raw.get("packInstance")),
            _optional_string(template.get("templateKey")),
            _optional_string(template.get("contentHash")),
        )

    result: dict[str, PlannedArtifactMetadata] = {}
    seen_paths: set[str] = set()
    for raw in artifacts_raw:
        if not isinstance(raw, dict):
            raise ArtifactVerificationError(
                "CLI_PLAN_ARTIFACT",
                "GenerationPlan artifact must be an object",
            )
        artifact_id = _string(raw.get("id"), "artifact.id")
        path = _string(raw.get("path"), "artifact.path")
        safe_artifact_path(path)
        job_id = _string(raw.get("jobId"), "artifact.jobId")
        if job_id not in job_order:
            raise ArtifactVerificationError(
                "CLI_PLAN_ARTIFACT",
                f"artifact {artifact_id!r} references unknown job",
            )
        if artifact_id in result or path in seen_paths:
            raise ArtifactVerificationError(
                "CLI_PLAN_ARTIFACT_DUPLICATE",
                "GenerationPlan artifact ids and paths must be unique",
            )
        semantic_ids = _strings(raw.get("semanticIds", []), "artifact.semanticIds")
        dependencies = _strings(raw.get("dependencies", []), "artifact.dependencies")
        subject_id, subject_kind, pack_id, pack_instance, template_key, template_hash = (
            job_subject[job_id]
        )
        result[artifact_id] = PlannedArtifactMetadata(
            artifact_id,
            path,
            ArtifactProvenance(
                job_id,
                job_order[job_id],
                semantic_ids,
                dependencies,
                subject_id,
                subject_kind,
                pack_id,
                pack_instance,
                template_key,
                template_hash,
            ),
        )
        seen_paths.add(path)
    return result


def verify_bundle_manifest(
    document: object,
    *,
    build_id: str,
    plan_hash: str,
    planned: dict[str, PlannedArtifactMetadata],
) -> tuple[dict[str, object], ...]:
    if not isinstance(document, dict):
        raise ArtifactVerificationError(
            "CLI_BUNDLE_MANIFEST",
            "bundle manifest must be a JSON object",
        )
    if document.get("version") != "dryv.bundle/v1":
        raise ArtifactVerificationError(
            "CLI_BUNDLE_VERSION",
            "bundle manifest version is unsupported",
        )
    if document.get("buildId") != build_id or document.get("planHash") != plan_hash:
        raise ArtifactVerificationError(
            "CLI_BUNDLE_IDENTITY",
            "bundle identity does not match the active build/plan",
        )
    raw = document.get("artifacts")
    if not isinstance(raw, list):
        raise ArtifactVerificationError(
            "CLI_BUNDLE_MANIFEST",
            "bundle artifacts must be an array",
        )
    entries: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for value in raw:
        if not isinstance(value, dict):
            raise ArtifactVerificationError(
                "CLI_BUNDLE_MANIFEST",
                "bundle artifact must be an object",
            )
        item = dict(value)
        artifact_id = _string(item.get("artifactId"), "artifactId")
        path = _string(item.get("path"), "path")
        safe_artifact_path(path)
        expected = planned.get(artifact_id)
        if expected is None or expected.path != path:
            raise ArtifactVerificationError(
                "CLI_BUNDLE_PLAN",
                f"bundle artifact {artifact_id!r} does not match GenerationPlan",
            )
        _verify_bundle_provenance(item, expected)
        if artifact_id in seen_ids or path in seen_paths:
            raise ArtifactVerificationError(
                "CLI_BUNDLE_DUPLICATE",
                "bundle artifact ids and paths must be unique",
            )
        seen_ids.add(artifact_id)
        seen_paths.add(path)
        entries.append(item)
    if seen_ids != set(planned):
        raise ArtifactVerificationError(
            "CLI_BUNDLE_INCOMPLETE",
            "bundle manifest does not contain exactly the planned artifacts",
        )
    return tuple(entries)


def _verify_bundle_provenance(
    item: dict[str, object],
    expected: PlannedArtifactMetadata,
) -> None:
    provenance = expected.provenance
    plan_index = item.get("planIndex")
    if (
        not isinstance(plan_index, int)
        or isinstance(plan_index, bool)
        or plan_index != provenance.plan_index
    ):
        raise ArtifactVerificationError(
            "CLI_BUNDLE_PROVENANCE",
            f"bundle artifact {expected.artifact_id!r} has an unexpected plan index",
        )
    if _strings(item.get("semanticIds", []), "semanticIds") != provenance.semantic_ids:
        raise ArtifactVerificationError(
            "CLI_BUNDLE_PROVENANCE",
            f"bundle artifact {expected.artifact_id!r} semantic ids do not match GenerationPlan",
        )
    expected_fields = (
        ("subjectId", provenance.subject_id),
        ("subjectKind", provenance.subject_kind),
        ("packId", provenance.pack_id),
        ("packInstance", provenance.pack_instance),
        ("templateKey", provenance.template_key),
        ("templateHash", provenance.template_hash),
    )
    for key, expected_value in expected_fields:
        actual = item.get(key)
        if actual != expected_value:
            raise ArtifactVerificationError(
                "CLI_BUNDLE_PROVENANCE",
                f"bundle artifact {expected.artifact_id!r} {key} does not match GenerationPlan",
            )


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ArtifactVerificationError(
            "CLI_ARTIFACT_METADATA",
            f"{name} must be a non-empty string",
        )
    return value


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _strings(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ArtifactVerificationError(
            "CLI_ARTIFACT_METADATA",
            f"{name} must be an array of strings",
        )
    return tuple(value)


__all__ = ["PlannedArtifactMetadata", "planned_artifacts", "verify_bundle_manifest"]
