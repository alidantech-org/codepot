from __future__ import annotations

import json

from .models import ArtifactPlan, GenerationPlan, ModuleCollection


def plan_to_document(plan: GenerationPlan) -> dict[str, object]:
    return {
        "artifacts": tuple(_artifact_document(item) for item in plan.artifacts),
        "diagnostics": plan.diagnostics.to_dict(),
        "project": plan.project_name,
        "ready": plan.ready,
    }


def plan_to_json(plan: GenerationPlan, *, pretty: bool = True) -> str:
    return json.dumps(
        plan_to_document(plan),
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        sort_keys=True,
    ) + ("\n" if pretty else "")


def explain_artifact(plan: GenerationPlan, identifier_or_path: str) -> dict[str, object]:
    matches = tuple(
        item
        for item in plan.artifacts
        if item.id == identifier_or_path or item.output_path == identifier_or_path
    )
    if len(matches) != 1:
        raise KeyError(f"artifact {identifier_or_path!r} is not uniquely planned")
    artifact = matches[0]
    document = _artifact_document(artifact)
    document["causes"] = {
        "groupId": artifact.group_id,
        "semanticId": artifact.semantic_id,
        "selection": artifact.selection_key,
        "template": artifact.template_id,
    }
    return document


def _artifact_document(artifact: ArtifactPlan) -> dict[str, object]:
    return {
        "engine": artifact.engine_id,
        "exports": _dependency_document(artifact.exports),
        "id": artifact.id,
        "imports": _dependency_document(artifact.imports),
        "kind": artifact.kind.value,
        "outputPath": artifact.output_path,
        "packId": artifact.pack_id,
        "packInstance": artifact.pack_instance,
        "selection": artifact.selection_key,
        "semanticId": artifact.semantic_id,
        "symbols": artifact.symbols,
        "target": artifact.target_id,
        "template": artifact.template_id,
    }


def _dependency_document(
    values: tuple[tuple[str, ModuleCollection], ...],
) -> dict[str, object]:
    return {
        key: tuple(
            {
                "artifactPath": item.artifact_path,
                "semanticId": item.semantic_id,
                "specifier": item.specifier,
                "symbols": item.symbols,
            }
            for item in collection.modules
        )
        for key, collection in values
    }
