from __future__ import annotations

import heapq
from collections import defaultdict
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import replace
from pathlib import Path, PurePosixPath
from typing import Any

from archives.codepotg.src.contracts.emission import (
    EmissionFile,
    EmissionPlan,
    EmissionResult,
    EmissionWriteResult,
)
from archives.codepotg.src.contracts.events import ProgressSink, RuntimeEvent
from archives.codepotg.src.contracts.paths import PathLifecycleMode
from archives.codepotg.src.core.errors import ConfigError
from archives.codepotg.src.emission.engine import (
    EmissionContextBuilder,
    import_planner_for_language,
)
from archives.codepotg.src.emission.graph_engine import _emission_file
from archives.codepotg.src.emission.graph_queue import (
    GraphQueueLimits,
    GraphQueueStats,
    GraphWriteCompletion,
    GraphWriteQueue,
    RenderedGraphFile,
    rendered_size,
)
from archives.codepotg.src.emission.paths.config_loader import load_path_config
from archives.codepotg.src.emission.paths.graph_planner import (
    PathGraphPlanningError,
    plan_path_graph,
)
from archives.codepotg.src.emission.planning import VirtualOutputRegistry
from archives.codepotg.src.emission.templates.renderer import render_template


def emit_graph_queued(
    contract: Any,
    *,
    progress: ProgressSink | None = None,
    limits: GraphQueueLimits | None = None,
) -> EmissionResult:
    """Plan and execute a named paths graph through bounded queues."""

    if contract.emit.template_root is None:
        raise ValueError("template_root is required for emission")
    template_root = contract.emit.template_root
    output_root = contract.emit.output_path
    path_config = load_path_config(template_root, strict=True)
    if not path_config.uses_graph:
        raise ValueError("emit_graph_queued requires a named paths graph")

    base_context = EmissionContextBuilder(contract).global_context()
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

    import_planner = import_planner_for_language(contract.lang.name)
    files: list[EmissionFile] = []
    for graph_file in graph.files:
        file = _emission_file(
            graph_file,
            registry=graph.registry,
            template_root=template_root,
            output_root=output_root,
            path_config=path_config,
            import_planner=import_planner,
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


def execute_queued_graph_emission(
    plan: EmissionPlan,
    *,
    registry: VirtualOutputRegistry,
    dry_run: bool = False,
    progress: ProgressSink | None = None,
    limits: GraphQueueLimits | None = None,
) -> EmissionResult:
    """Render ready nodes concurrently and write through one bounded writer."""

    queue_limits = limits or GraphQueueLimits()
    _validate_plan(plan)
    refusals = tuple(file for file in plan.files if file.refusal_reason)
    if refusals:
        details = "\n".join(
            f"  - {file.output_path}: {file.refusal_reason}" for file in refusals
        )
        raise ConfigError(f"Unsafe template writes refused:\n{details}")

    if dry_run:
        _notify(
            progress,
            "emission_dry_run",
            f"Dry run skipped {len(plan.files)} files",
            total=len(plan.files),
        )
        return EmissionResult(
            plan=plan,
            write_result=EmissionWriteResult(
                skipped=tuple(file.output_path for file in plan.files),
            ),
            output_registry=registry,
            queue_stats=GraphQueueStats(),
        )

    by_path = {_relative(file, plan.output_root): file for file in plan.files}
    dependencies = {
        path: set(file.depends_on)
        for path, file in by_path.items()
    }
    dependants: dict[str, set[str]] = defaultdict(set)
    for path, required in dependencies.items():
        for dependency in required:
            if dependency not in by_path:
                raise PathGraphPlanningError(
                    f"Output '{path}' depends on unknown output '{dependency}'."
                )
            dependants[dependency].add(path)

    ready = [path for path, required in dependencies.items() if not required]
    heapq.heapify(ready)
    active: dict[Future[RenderedGraphFile], str] = {}
    submitted: set[str] = set()
    written: set[str] = set()
    pending_writes = 0
    accumulator = _WriteAccumulator()
    writer = GraphWriteQueue(limits=queue_limits)
    writer.start()

    try:
        with ThreadPoolExecutor(
            max_workers=queue_limits.max_render_workers,
            thread_name_prefix="codepotg-render",
        ) as render_pool:
            while len(written) < len(by_path):
                while ready and len(active) < queue_limits.max_render_workers:
                    path = heapq.heappop(ready)
                    if path in submitted:
                        continue
                    submitted.add(path)
                    file = by_path[path]
                    _notify(
                        progress,
                        "file_rendering",
                        f"Rendering: {file.output_path}",
                        current=len(submitted),
                        total=len(by_path),
                    )
                    active[render_pool.submit(_render_file, file, plan.template_root)] = path

                if active:
                    done, _ = wait(
                        tuple(active),
                        timeout=queue_limits.wait_timeout_seconds,
                        return_when=FIRST_COMPLETED,
                    )
                    for future in done:
                        path = active.pop(future)
                        item = future.result()
                        _notify(
                            progress,
                            "file_rendered",
                            f"Rendered: {item.file.output_path}",
                            current=len(submitted),
                            total=len(by_path),
                        )
                        _notify(
                            progress,
                            "file_queued",
                            f"Queued for write: {item.file.output_path}",
                            current=pending_writes + 1,
                            total=len(by_path),
                        )
                        writer.submit(item)
                        pending_writes += 1

                completion = writer.completion(block=False)
                while completion is not None:
                    pending_writes -= 1
                    _complete_write(
                        completion,
                        output_root=plan.output_root,
                        registry=registry,
                        written=written,
                        dependencies=dependencies,
                        dependants=dependants,
                        ready=ready,
                        accumulator=accumulator,
                        progress=progress,
                        total=len(by_path),
                    )
                    completion = writer.completion(block=False)

                if not active and not ready and pending_writes:
                    completion = writer.completion(block=True)
                    if completion is not None:
                        pending_writes -= 1
                        _complete_write(
                            completion,
                            output_root=plan.output_root,
                            registry=registry,
                            written=written,
                            dependencies=dependencies,
                            dependants=dependants,
                            ready=ready,
                            accumulator=accumulator,
                            progress=progress,
                            total=len(by_path),
                        )

                if not active and not ready and not pending_writes and len(written) < len(by_path):
                    blocked = sorted(set(by_path) - written)
                    raise PathGraphPlanningError(
                        "Graph scheduler has no ready work; blocked outputs: "
                        + ", ".join(blocked)
                    )
    finally:
        queue_stats = writer.close()

    _notify(
        progress,
        "emission_complete",
        f"Completed {len(plan.files)} graph outputs",
        total=len(plan.files),
    )
    return EmissionResult(
        plan=plan,
        write_result=accumulator.result(),
        output_registry=registry,
        queue_stats=queue_stats,
    )


def _render_file(file: EmissionFile, template_root: Path) -> RenderedGraphFile:
    if file.lifecycle == PathLifecycleMode.IMMUTABLE and file.output_path.exists():
        return RenderedGraphFile(
            file=file,
            content=None,
            estimated_bytes=1,
            immutable_existing=True,
        )
    if file.is_template:
        content: str | bytes = render_template(template_root, file.template_path, file.context)
    else:
        content = (template_root / file.template_path).read_bytes()
    return RenderedGraphFile(
        file=file,
        content=content,
        estimated_bytes=rendered_size(content),
    )


def _complete_write(
    completion: GraphWriteCompletion,
    *,
    output_root: Path,
    registry: VirtualOutputRegistry,
    written: set[str],
    dependencies: dict[str, set[str]],
    dependants: dict[str, set[str]],
    ready: list[str],
    accumulator: _WriteAccumulator,
    progress: ProgressSink | None,
    total: int,
) -> None:
    file = completion.item.file
    path = _relative(file, output_root)
    if path in written:
        raise PathGraphPlanningError(f"Output completed more than once: {path}")
    written.add(path)
    registry.mark_written_path(PurePosixPath(path))
    accumulator.add(completion.result)
    stage, action = _write_event(completion.result)
    _notify(
        progress,
        stage,
        f"{action}: {file.output_path}",
        current=len(written),
        total=total,
    )
    for dependant in sorted(dependants.get(path, ())):
        dependencies[dependant].discard(path)
        if not dependencies[dependant]:
            heapq.heappush(ready, dependant)


def _validate_plan(plan: EmissionPlan) -> None:
    paths = [_relative(file, plan.output_root) for file in plan.files]
    if len(paths) != len(set(paths)):
        raise PathGraphPlanningError("Graph emission plan contains duplicate output paths.")


def _relative(file: EmissionFile, output_root: Path) -> str:
    return file.output_path.relative_to(output_root).as_posix()


class _WriteAccumulator:
    def __init__(self) -> None:
        self.created: list[Path] = []
        self.updated: list[Path] = []
        self.unchanged: list[Path] = []
        self.skipped: list[Path] = []
        self.immutable_created: list[Path] = []
        self.immutable_skipped: list[Path] = []
        self.refused: list[Path] = []
        self.refusal_reasons: dict[Path, str] = {}

    def add(self, result: EmissionWriteResult) -> None:
        self.created.extend(result.created)
        self.updated.extend(result.updated)
        self.unchanged.extend(result.unchanged)
        self.skipped.extend(result.skipped)
        self.immutable_created.extend(result.immutable_created)
        self.immutable_skipped.extend(result.immutable_skipped)
        self.refused.extend(result.refused)
        self.refusal_reasons.update(result.refusal_reasons)

    def result(self) -> EmissionWriteResult:
        return EmissionWriteResult(
            created=tuple(self.created),
            updated=tuple(self.updated),
            unchanged=tuple(self.unchanged),
            skipped=tuple(self.skipped),
            immutable_created=tuple(self.immutable_created),
            immutable_skipped=tuple(self.immutable_skipped),
            refused=tuple(self.refused),
            refusal_reasons=dict(self.refusal_reasons),
        )


def _write_event(result: EmissionWriteResult) -> tuple[str, str]:
    if result.created:
        return "file_written", "Created"
    if result.updated:
        return "file_written", "Updated"
    if result.unchanged:
        return "file_unchanged", "Unchanged"
    if result.immutable_skipped:
        return "file_immutable_skipped", "Skipped immutable existing"
    return "file_skipped", "Skipped"


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
