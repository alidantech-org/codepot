from __future__ import annotations

from pathlib import Path

from dryv.api import CancellationToken, OperationResult
from dryv.generation.models import GenerationData
from dryv.ports import ManagedOutputWriter, ManagedWriteReport

from .facade import DryvRuntime
from .plugins import RuntimePlugins


def generate_to_files(
    project_file: str | Path = "dryv.yaml",
    *,
    destination: str | Path | None = None,
    plugins: RuntimePlugins | None = None,
    cancellation: CancellationToken | None = None,
    writer: ManagedOutputWriter | None = None,
) -> tuple[OperationResult[GenerationData], ManagedWriteReport | None]:
    """Compatibility wrapper around :class:`DryvRuntime`.

    New hosts should construct one runtime and reuse it for planning, generation,
    inspection, and writing.
    """

    runtime = DryvRuntime(plugins=plugins if plugins is not None else RuntimePlugins.discover())
    return runtime.generate_to_files(
        project_file,
        destination=destination,
        cancellation=cancellation,
        writer=writer,
    )
