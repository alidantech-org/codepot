from __future__ import annotations

from dryv_cli.generation import GenerationProgress

from .console import Console


class ProgressPrinter:
    def __init__(self, console: Console) -> None:
        self.console = console

    def __call__(self, progress: GenerationProgress) -> None:
        if progress.type == "artifact.chunk":
            return
        message = progress.message or progress.type
        if progress.subject:
            message += f" [{progress.subject}]"
        details = " ".join(f"{key}={value}" for key, value in sorted(progress.details.items()))
        if details:
            message += f" · {details}"
        self.console.write(message)


__all__ = ["ProgressPrinter"]
