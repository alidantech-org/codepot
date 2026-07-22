from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from constants.files import (
    DIR_GENERATOR,
    DIR_LANGUAGES,
    DIR_SRC,
    DIR_TEMPLATES,
    DIR_TESTS,
    ERR_PROJECT_ROOT_NOT_FOUND,
    FILE_PYPROJECT,
)
from core.errors import PathResolutionError


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @property
    def src(self) -> Path:
        return self.root / DIR_SRC

    @property
    def tests(self) -> Path:
        return self.root / DIR_TESTS

    @property
    def templates(self) -> Path:
        return self.src / DIR_TEMPLATES

    @property
    def language_templates(self) -> Path:
        return self.src / DIR_LANGUAGES

    @property
    def pyproject(self) -> Path:
        return self.root / FILE_PYPROJECT

    @classmethod
    def from_cwd(cls, cwd: Path | None = None) -> "ProjectPaths":
        current = (cwd or Path.cwd()).resolve()

        # If command is run inside generator/, detect it directly.
        if (current / FILE_PYPROJECT).exists() and (current / DIR_SRC).exists():
            return cls(root=current)

        # If command is run from parent repo, detect generator/.
        generator_root = current / DIR_GENERATOR
        if (generator_root / FILE_PYPROJECT).exists() and (generator_root / DIR_SRC).exists():
            return cls(root=generator_root.resolve())

        raise PathResolutionError(ERR_PROJECT_ROOT_NOT_FOUND)

    def resolve_input(self, value: str | Path) -> Path:
        path = Path(value)

        if path.is_absolute():
            return path.resolve()

        cwd_path = (Path.cwd() / path).resolve()
        if cwd_path.exists():
            return cwd_path

        root_path = (self.root / path).resolve()
        if root_path.exists():
            return root_path

        return cwd_path

    def resolve_output(self, value: str | Path) -> Path:
        path = Path(value)

        if path.is_absolute():
            return path.resolve()

        return (Path.cwd() / path).resolve()
