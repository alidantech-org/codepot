from __future__ import annotations

from pathlib import Path

from .process import AuthorProcess
from .result import AuthorResult


class AuthorClient:
    def __init__(self, process: AuthorProcess | None = None) -> None:
        self.process = process or AuthorProcess()

    def compile(
        self,
        target: str,
        *,
        project_root: Path,
        representation: str = "json",
    ) -> AuthorResult:
        return self.process.compile(target, project_root=project_root, representation=representation)

    def validate(self, target: str, *, project_root: Path) -> AuthorResult:
        return self.process.compile(target, project_root=project_root, representation="json")


__all__ = ["AuthorClient"]
