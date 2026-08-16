from __future__ import annotations

from dataclasses import dataclass

from dryv.runtime import RuntimeInput, RuntimePack, RuntimePackResource

from dryv_api.contracts import CreateBuildRequest

from .store import ResourceStore


@dataclass(frozen=True, slots=True)
class NormalizedBuild:
    runtime_input: RuntimeInput
    resources: ResourceStore


def normalize_build(request: CreateBuildRequest) -> NormalizedBuild:
    """Normalize uploaded bytes into Runtime input without interpreting Dryv semantics."""

    store = ResourceStore()
    store.add(request.project)
    store.add(request.canonical_ir)
    for upload in request.resources:
        store.add(upload)

    runtime_packs: list[RuntimePack] = []
    for bundle in request.packs:
        manifest = store.add(bundle.manifest)
        resources: list[RuntimePackResource] = []
        for item in bundle.resources:
            stored = store.add(item.resource)
            resources.append(RuntimePackResource(item.relative_path, stored.resource_id))
        runtime_packs.append(
            RuntimePack(
                bundle.instance_name,
                manifest.resource_id,
                tuple(sorted(resources, key=lambda item: item.relative_path)),
            )
        )

    runtime_input = RuntimeInput(
        build_id=request.build_id,
        project_resource_id=request.project.resource_id,
        canonical_ir_resource_id=request.canonical_ir.resource_id,
        resources=tuple(item.runtime_resource() for item in store.resources()),
        packs=tuple(sorted(runtime_packs, key=lambda item: item.instance_name)),
    )
    return NormalizedBuild(runtime_input, store)


__all__ = ["NormalizedBuild", "normalize_build"]
