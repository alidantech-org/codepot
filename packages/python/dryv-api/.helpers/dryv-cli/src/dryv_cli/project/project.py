from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import ProjectLocators


class ProjectError(ValueError):
    def __init__(self, code: str, message: str, *, path: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path


@dataclass(frozen=True, slots=True)
class LocalProject:
    root: Path
    config_path: Path
    config_bytes: bytes
    config_media_type: str
    locators: ProjectLocators


__all__ = ["LocalProject", "ProjectError"]
