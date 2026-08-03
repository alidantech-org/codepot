from __future__ import annotations

from pathlib import Path

from contracts.emission import EmissionFile, EmissionPlan
from contracts.paths import PathLifecycleMode
from emission.graph_queue import GraphQueueLimits
from emission.planning import OutputStatus, VirtualOutputRegistry
from emission.queued_graph_engine import execute_queued_graph_emission


def test_queued_graph_writes_dependencies_before_dependants_and_marks_registry(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    output = tmp_path / "generated"
    templates.mkdir()
    (templates / "leaf.txt.j2").write_text("leaf\n", encoding="utf-8")
    (templates / "barrel.txt.j2").write_text("barrel\n", encoding="utf-8")
    leaf = _file(
        templates,
        output,
        template="leaf.txt.j2",
        relative="leaf.txt",
        node="leaf",
        source="leaf:one",
    )
    barrel = _file(
        templates,
        output,
        template="barrel.txt.j2",
        relative="index.txt",
        node="barrel",
        source="barrel:all",
        depends_on=("leaf.txt",),
        is_barrel=True,
    )
    registry = _registry(leaf, barrel, output_root=output)
    events = []

    result = execute_queued_graph_emission(
        EmissionPlan(
            language="text",
            template_root=templates,
            output_root=output,
            files=(barrel, leaf),
        ),
        registry=registry,
        progress=events.append,
        limits=GraphQueueLimits(max_render_workers=2, max_pending_files=1),
    )

    assert set(result.write_result.created) == {
        output / "leaf.txt",
        output / "index.txt",
    }
    assert registry.get_by_path("leaf.txt").status == OutputStatus.WRITTEN
    assert registry.get_by_path("index.txt").status == OutputStatus.WRITTEN
    assert result.queue_stats.pending_files_high_water <= 1
    assert result.queue_stats.files_written == 2

    queued_leaf = next(
        index
        for index, event in enumerate(events)
        if event.stage == "file_queued" and "leaf.txt" in event.message
    )
    written_leaf = next(
        index
        for index, event in enumerate(events)
        if event.stage == "file_written" and "leaf.txt" in event.message
    )
    rendering_barrel = next(
        index
        for index, event in enumerate(events)
        if event.stage == "file_rendering" and "index.txt" in event.message
    )
    assert queued_leaf < written_leaf < rendering_barrel


def test_queued_graph_dry_run_keeps_registry_planned(tmp_path: Path) -> None:
    templates = tmp_path / "templates"
    output = tmp_path / "generated"
    templates.mkdir()
    (templates / "file.txt.j2").write_text("value\n", encoding="utf-8")
    file = _file(
        templates,
        output,
        template="file.txt.j2",
        relative="file.txt",
        node="files",
        source="file:one",
    )
    registry = _registry(file, output_root=output)

    result = execute_queued_graph_emission(
        EmissionPlan(
            language="text",
            template_root=templates,
            output_root=output,
            files=(file,),
        ),
        registry=registry,
        dry_run=True,
    )

    assert result.write_result.skipped == (output / "file.txt",)
    assert not (output / "file.txt").exists()
    assert registry.get_by_path("file.txt").status == OutputStatus.PLANNED
    assert result.queue_stats.files_written == 0


def test_immutable_existing_provider_releases_dependant(tmp_path: Path) -> None:
    templates = tmp_path / "templates"
    output = tmp_path / "generated"
    templates.mkdir()
    output.mkdir()
    (templates / "provider.txt.j2").write_text("new provider\n", encoding="utf-8")
    (templates / "consumer.txt.j2").write_text("consumer\n", encoding="utf-8")
    (output / "provider.txt").write_text("existing provider\n", encoding="utf-8")
    provider = _file(
        templates,
        output,
        template="provider.txt.j2",
        relative="provider.txt",
        node="provider",
        source="provider:one",
        lifecycle=PathLifecycleMode.IMMUTABLE,
    )
    consumer = _file(
        templates,
        output,
        template="consumer.txt.j2",
        relative="consumer.txt",
        node="consumer",
        source="consumer:one",
        depends_on=("provider.txt",),
    )
    registry = _registry(provider, consumer, output_root=output)

    result = execute_queued_graph_emission(
        EmissionPlan(
            language="text",
            template_root=templates,
            output_root=output,
            files=(consumer, provider),
        ),
        registry=registry,
    )

    assert result.write_result.immutable_skipped == (output / "provider.txt",)
    assert result.write_result.created == (output / "consumer.txt",)
    assert (output / "provider.txt").read_text(encoding="utf-8") == "existing provider\n"
    assert registry.get_by_path("provider.txt").status == OutputStatus.WRITTEN
    assert registry.get_by_path("consumer.txt").status == OutputStatus.WRITTEN


def _file(
    templates: Path,
    output: Path,
    *,
    template: str,
    relative: str,
    node: str,
    source: str,
    depends_on: tuple[str, ...] = (),
    lifecycle: PathLifecycleMode = PathLifecycleMode.MANAGED,
    is_barrel: bool = False,
) -> EmissionFile:
    return EmissionFile(
        template_path=Path(template),
        output_path=output / relative,
        context={},
        lifecycle=lifecycle,
        node_key=node,
        selection="selection",
        source_key=source,
        depends_on=depends_on,
        is_barrel=is_barrel,
    )


def _registry(
    *files: EmissionFile,
    output_root: Path,
) -> VirtualOutputRegistry:
    registry = VirtualOutputRegistry()
    for file in files:
        relative = file.output_path.relative_to(output_root)
        registry.register(
            selection=file.selection,
            emission=file.node_key,
            source_key=file.source_key,
            source_ref=file.source_ref,
            template_path=file.template_path,
            output_path=relative,
        )
    return registry
