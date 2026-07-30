from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from archives.codepotg.src.contracts.emission import EmissionFile, EmissionPlan, EmissionResult
from archives.codepotg.src.contracts.events import ProgressSink, RuntimeEvent
from archives.codepotg.src.core.errors import ConfigError
from archives.codepotg.src.core.system_resources import tune_runtime
from archives.codepotg.src.emission.contexts.bounded import bounded_graph_context
from archives.codepotg.src.emission.engine import import_planner_for_language
from archives.codepotg.src.emission.graph_engine import _emission_file
from archives.codepotg.src.emission.graph_queue import GraphQueueLimits
from archives.codepotg.src.emission.paths.config_loader import load_path_config
from archives.codepotg.src.emission.paths.graph_planner import plan_path_graph
from archives.codepotg.src.emission.queued_graph_engine import execute_queued_graph_emission
from archives.codepotg.src.openapi.jsonl import JsonlLazyResolver, LazyJsonlRecord


def emit_bounded_graph(
    contract: Any,
    *,
    progress: ProgressSink | None = None,
    limits: GraphQueueLimits | None = None,
) -> EmissionResult:
    """Plan with hidden selection roots and render only bounded globals."""
    if contract.emit.template_root is None:
        raise ValueError("template_root is required for emission")
    template_root = contract.emit.template_root
    output_root = contract.emit.output_path
    path_config = load_path_config(template_root, strict=True)
    if not path_config.uses_graph:
        raise ValueError("emit_bounded_graph requires a named paths graph")

    resolver = _resolver_from_contract(contract)
    try:
        base_context = bounded_graph_context(contract)
        _notify(progress, "selection_started", "Resolving named selections")
        graph = plan_path_graph(
            config=path_config,
            base_context=base_context,
            template_root=template_root,
        )
        _notify(
            progress,
            "selection_resolved",
            f"Resolved {len(path_config.selections)} selection(s)",
            total=len(path_config.selections),
        )

        planner = import_planner_for_language(contract.lang.name)
        files: list[EmissionFile] = []
        for graph_file in graph.files:
            file = _emission_file(
                graph_file,
                registry=graph.registry,
                template_root=template_root,
                output_root=output_root,
                path_config=path_config,
                import_planner=planner,
                package_name=contract.lang.package.name,
            )
            if not file.is_template and not path_config.allow_raw_files:
                raise ConfigError(
                    f"Raw template files are disabled but graph node '{file.node_key}' "
                    f"uses '{file.template_path}'."
                )
            exact_dependencies = tuple(
                sorted(set(file.depends_on) | set(file.dependency_outputs.values()))
            )
            context = dict(file.context)
            sources = _lazy_sources(
                resolver,
                output_root=output_root,
                file=file,
                registry=graph.registry,
            )
            context["source"] = sources[0] if len(sources) == 1 else None
            context["sources"] = sources
            context["resolve"] = resolver
            context["resolver_stats"] = resolver.stats()
            files.append(
                replace(
                    file,
                    context=context,
                    depends_on=exact_dependencies,
                )
            )

        plan = EmissionPlan(
            language=contract.lang.name,
            template_root=template_root,
            output_root=output_root,
            files=tuple(files),
        )
        for index, file in enumerate(plan.files, start=1):
            _notify(
                progress,
                "file_planned",
                f"Planned: {file.output_path}",
                current=index,
                total=len(plan.files),
            )

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
        result = execute_queued_graph_emission(
            plan,
            registry=graph.registry,
            dry_run=contract.emit.dry_run,
            progress=progress,
            limits=effective_limits,
        )
        _notify(
            progress,
            "resolver_complete",
            f"Lazy JSONL resolver loaded {resolver.load_count} record(s)",
        )
        return result
    finally:
        resolver.close()


def _resolver_from_contract(contract: Any) -> JsonlLazyResolver:
    cache = contract.emit.meta.get("jsonl_cache")
    if not isinstance(cache, str | Path):
        raise ConfigError("Graph emission requires emit.meta.jsonl_cache")
    return JsonlLazyResolver(Path(cache))


def _lazy_sources(
    resolver: JsonlLazyResolver,
    *,
    output_root: Path,
    file: EmissionFile,
    registry: Any,
) -> tuple[LazyJsonlRecord, ...]:
    relative = file.output_path.relative_to(output_root)
    output = registry.get_by_path(relative)
    if output is None:
        return ()
    values: list[LazyJsonlRecord] = []
    for ref in output.refs:
        source = resolver.ref(ref)
        if source is not None:
            values.append(source)
    if not values and file.source_key:
        source = resolver.key(file.source_key)
        if source is not None:
            values.append(source)
    return tuple(values)


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
