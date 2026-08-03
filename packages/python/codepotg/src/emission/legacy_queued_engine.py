"""Adaptive queued runtime for legacy folder-based template packs.

The established ``emission.engine`` planning API remains compatible and eager for
callers that inspect rendered plan content. Normal generation uses this module to
build the same file/context plan without rendering, then renders concurrently and
writes bounded batches atomically.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from archives.codepotg.src.contracts.emission import (
    EmissionFile,
    EmissionPlan,
    EmissionResult,
    TemplateContext,
)
from archives.codepotg.src.contracts.events import ProgressSink, RuntimeEvent
from archives.codepotg.src.contracts.normalized_document_contract import (
    build_normalized_document_contract,
)
from archives.codepotg.src.core.system_resources import tune_runtime
from archives.codepotg.src.emission import engine as legacy
from archives.codepotg.src.emission.graph_queue import GraphQueueLimits
from archives.codepotg.src.emission.paths.config_loader import load_path_config
from archives.codepotg.src.emission.planning import VirtualOutputRegistry
from archives.codepotg.src.emission.queued_graph_engine import execute_queued_graph_emission
from archives.codepotg.src.emission.templates.scanner import scan_templates


class _LegacyOutputRegistry(VirtualOutputRegistry):
    """No-op status registry for legacy outputs that have no virtual graph entry."""

    def mark_written_path(self, output_path: str | Path | PurePosixPath):
        return None


def emit_legacy_queued(
    contract: Any,
    *,
    progress: ProgressSink | None = None,
    limits: GraphQueueLimits | None = None,
) -> EmissionResult:
    """Plan legacy outputs without rendering, then render/write through queues."""
    plan = build_legacy_queued_plan(contract, progress=progress)
    tuning = tune_runtime(
        _source_size_from_contract(contract),
        planned_files=len(plan.files),
    )
    effective_limits = limits or GraphQueueLimits(
        max_render_workers=tuning.render_workers,
        max_write_workers=tuning.write_workers,
        max_pending_files=tuning.pending_files,
        max_pending_bytes=tuning.pending_render_bytes,
        write_batch_files=tuning.write_batch_files,
        write_batch_bytes=tuning.write_batch_bytes,
    )
    _notify(
        progress,
        "runtime_tuned",
        tuning.summary(),
        total=len(plan.files),
    )
    return execute_queued_graph_emission(
        plan,
        registry=_LegacyOutputRegistry(),
        dry_run=contract.emit.dry_run,
        progress=progress,
        limits=effective_limits,
    )


def build_legacy_queued_plan(
    contract: Any,
    *,
    progress: ProgressSink | None = None,
) -> EmissionPlan:
    """Build the established legacy output plan without eager template rendering."""
    if contract.emit.template_root is None:
        raise ValueError("template_root is required for emission")

    template_root = contract.emit.template_root
    output_root = contract.emit.output_path

    _notify(progress, "loading_path_config", f"Loading path config from {template_root}")
    path_config = load_path_config(template_root)

    _notify(progress, "scanning_templates", f"Scanning templates in {template_root}")
    descriptors = scan_templates(template_root)

    base_context = _legacy_template_context(contract)
    files: list[EmissionFile] = []

    for descriptor in descriptors:
        for context in legacy._contexts_for_descriptor(
            descriptor,
            base_context,
            path_config,
        ):
            output_path = legacy._resolve_output_path(
                descriptor=descriptor,
                context=context,
                output_root=output_root,
                template_extension=path_config.template_extension,
            )
            context = legacy._context_with_file(
                descriptor=descriptor,
                context=context,
                output_path=output_path,
                output_root=output_root,
                path_config=path_config,
            )
            folder_key = legacy._descriptor_folder_key(descriptor)
            lifecycle = legacy._lifecycle_for_folder(folder_key, path_config)
            refusal_reason = legacy._write_refusal_reason(
                output_path=output_path,
                output_root=output_root,
                lifecycle=lifecycle,
                policy=path_config.write_policy,
            )
            files.append(
                EmissionFile(
                    template_path=descriptor.relative_path,
                    output_path=output_path,
                    context=context,
                    content=None,
                    group=legacy._descriptor_group(descriptor),
                    is_template=legacy._is_jinja_template(
                        descriptor.relative_path,
                        template_extension=path_config.template_extension,
                    ),
                    compare_mode=legacy._compare_mode_for_output(output_path),
                    lifecycle=lifecycle,
                    folder_key=folder_key,
                    refusal_reason=refusal_reason,
                )
            )

    files = legacy._resolve_file_contexts(
        files=files,
        output_root=output_root,
        path_config=path_config,
        progress=progress,
        contract=contract,
    )

    _notify(
        progress,
        "emission_plan_created",
        f"Planned {len(files)} files without eager rendering",
        total=len(files),
    )
    return EmissionPlan(
        language=contract.lang.name,
        template_root=template_root,
        output_root=output_root,
        files=tuple(files),
    )


def _legacy_template_context(contract: Any) -> TemplateContext:
    """Expose normalized public roots to legacy packs during graph migration."""
    context = legacy.EmissionContextBuilder(contract).global_context()
    api_meta = getattr(getattr(contract, "api", None), "meta", {})
    meta: Mapping[str, Any] = api_meta if isinstance(api_meta, Mapping) else {}
    context.update(
        {
            "document_contract": build_normalized_document_contract(contract.api.raw),
            "normalized": meta.get("normalized"),
            "domains": meta.get("normalized_domains"),
            "schema_contract": meta.get("normalized_schemas"),
            "codegen_contract": meta.get("normalized_codegen"),
            "entity_contract": meta.get("normalized_entities"),
            "frontend_contract": meta.get("normalized_frontends"),
        }
    )
    return context


def _source_size_from_contract(contract: Any) -> int:
    value = contract.emit.meta.get("jsonl_source_size", 0)
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _notify(
    progress: ProgressSink | None,
    stage: str,
    message: str,
    *,
    level: str = "info",
    current: int | None = None,
    total: int | None = None,
) -> None:
    if progress is None:
        return
    progress(
        RuntimeEvent(
            stage=stage,
            message=message,
            level=level,
            current=current,
            total=total,
        )
    )
