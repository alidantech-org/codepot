from __future__ import annotations

from pathlib import Path

from dryv.api import CancellationToken, OperationResult
from dryv.application.write import generate_to_files as _generate_to_files
from dryv.generation.models import GenerationData
from dryv.infrastructure import ManagedFilesystemWriter
from dryv.ports import ManagedOutputWriter, ManagedWriteReport
from dryv.runtime.plugins import RuntimePlugins


def generate_to_files(
    project_file: str | Path = "dryv.yaml",
    *,
    destination: str | Path | None = None,
    plugins: RuntimePlugins | None = None,
    cancellation: CancellationToken | None = None,
    writer: ManagedOutputWriter | None = None,
) -> tuple[OperationResult[GenerationData], ManagedWriteReport | None]:
    selected_writer = writer if writer is not None else ManagedFilesystemWriter()
    return _generate_to_files(
        project_file,
        writer=selected_writer,
        destination=destination,
        plugins=plugins,
        cancellation=cancellation,
    )
