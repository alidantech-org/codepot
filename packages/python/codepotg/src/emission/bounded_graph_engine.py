from __future__ import annotations

from dataclasses import replace
from typing import Any

from contracts.emission import EmissionFile, EmissionPlan, EmissionResult
from contracts.events import ProgressSink, RuntimeEvent
from core.errors import ConfigError
from emission.contexts.bounded import bounded_graph_context
from emission.engine import import_planner_for_language
from emission.graph_engine import _emission_file
from emission.graph_queue import GraphQueueLimits
from emission.paths.config_loader import load_path_config
from emission.paths.graph_planner import plan_path_graph
from emission.queued_graph_engine import execute_queued_graph_emission


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
        files.append(replace(file, depends_on=exact_dependencies))

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

    return execute_queued_graph_emission(
        plan,
        registry=graph.registry,
        dry_run=contract.emit.dry_run,
        progress=progress,
        limits=limits,
    )


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
