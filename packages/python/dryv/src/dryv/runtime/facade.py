from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from dryv.api import CancellationToken, OperationResult
from dryv.application.generate import generate as _generate
from dryv.application.write import generate_to_files as _generate_to_files
from dryv.generation import GenerationData
from dryv.infrastructure import ManagedFilesystemWriter
from dryv.ports import ManagedOutputWriter, ManagedWriteReport
from dryv.versions import CORE_VERSION

from .models import RuntimePluginInfo, RuntimeSnapshot
from .plugins import RuntimePlugins

WriterFactory = Callable[[], ManagedOutputWriter]


def _managed_writer_factory() -> ManagedOutputWriter:
    return ManagedFilesystemWriter()


@dataclass(frozen=True, slots=True)
class DryvRuntime:
    """The primary in-process interface for planning and generation.

    A runtime owns one immutable plugin graph. Frontends may create separate runtime
    instances for isolation, inject a test/plugin graph, or use ``discover()`` to load
    installed entry points.
    """

    plugins: RuntimePlugins
    writer_factory: WriterFactory = _managed_writer_factory

    @classmethod
    def discover(cls, *, writer_factory: WriterFactory = _managed_writer_factory) -> Self:
        return cls(plugins=RuntimePlugins.discover(), writer_factory=writer_factory)

    def snapshot(self) -> RuntimeSnapshot:
        plugins: list[RuntimePluginInfo] = []

        for adapter in self.plugins.source_adapters:
            descriptor = adapter.plugin
            plugins.append(
                RuntimePluginInfo(
                    id=descriptor.id,
                    category=descriptor.category,
                    distribution=descriptor.distribution,
                    version=str(descriptor.version),
                    aliases=descriptor.aliases,
                    capabilities=descriptor.capabilities,
                )
            )

        for adapter in self.plugins.target_adapters:
            descriptor = adapter.plugin
            provided = tuple(
                sorted(
                    f"{target.id}: {', '.join(target.extensions)}"
                    for target in adapter.targets
                )
            )
            plugins.append(
                RuntimePluginInfo(
                    id=descriptor.id,
                    category=descriptor.category,
                    distribution=descriptor.distribution,
                    version=str(descriptor.version),
                    aliases=descriptor.aliases,
                    capabilities=descriptor.capabilities,
                    provides=provided,
                )
            )

        for engine in self.plugins.template_engines:
            descriptor = engine.plugin
            plugins.append(
                RuntimePluginInfo(
                    id=descriptor.id,
                    category=descriptor.category,
                    distribution=descriptor.distribution,
                    version=str(descriptor.version),
                    aliases=descriptor.aliases,
                    capabilities=descriptor.capabilities,
                    provides=tuple(sorted(engine.suffixes)),
                )
            )

        return RuntimeSnapshot(
            core_version=str(CORE_VERSION),
            plugins=tuple(sorted(plugins, key=lambda item: (item.category.value, item.id))),
        )

    def plan(
        self,
        project_file: str | Path = "dryv.yaml",
        *,
        cancellation: CancellationToken | None = None,
    ) -> OperationResult[GenerationData]:
        return _generate(
            project_file,
            plugins=self.plugins,
            cancellation=cancellation,
            dry_run=True,
        )

    def generate(
        self,
        project_file: str | Path = "dryv.yaml",
        *,
        cancellation: CancellationToken | None = None,
    ) -> OperationResult[GenerationData]:
        return _generate(
            project_file,
            plugins=self.plugins,
            cancellation=cancellation,
            dry_run=False,
        )

    def generate_to_files(
        self,
        project_file: str | Path = "dryv.yaml",
        *,
        destination: str | Path | None = None,
        cancellation: CancellationToken | None = None,
        writer: ManagedOutputWriter | None = None,
    ) -> tuple[OperationResult[GenerationData], ManagedWriteReport | None]:
        selected_writer = writer if writer is not None else self.writer_factory()
        return _generate_to_files(
            project_file,
            writer=selected_writer,
            destination=destination,
            plugins=self.plugins,
            cancellation=cancellation,
        )


def create_runtime(
    *,
    plugins: RuntimePlugins | None = None,
    writer_factory: WriterFactory = _managed_writer_factory,
) -> DryvRuntime:
    """Create one isolated runtime, discovering installed plugins when omitted."""

    return DryvRuntime(
        plugins=plugins if plugins is not None else RuntimePlugins.discover(),
        writer_factory=writer_factory,
    )
