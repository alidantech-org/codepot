from __future__ import annotations

from pathlib import Path

from .config import load_locators
from .project import LocalProject, ProjectError

_CONFIG_NAMES = ("dryv.yaml", "dryv.yml", "dryv.json")


def discover_project(start: str | Path = ".") -> LocalProject:
    current = Path(start).resolve()
    if current.is_file():
        current = current.parent
    for directory in (current, *current.parents):
        matches = tuple(directory / name for name in _CONFIG_NAMES if (directory / name).is_file())
        if len(matches) > 1:
            names = ", ".join(path.name for path in matches)
            raise ProjectError("CLI_PROJECT_AMBIGUOUS", f"multiple Dryv project files found: {names}")
        if matches:
            path = matches[0]
            content = path.read_bytes()
            media_type = "application/dryv+json" if path.suffix == ".json" else "application/dryv+yaml"
            return LocalProject(directory, path, content, media_type, load_locators(content, media_type))
    raise ProjectError("CLI_PROJECT_MISSING", "no dryv.yaml, dryv.yml, or dryv.json was found")


__all__ = ["discover_project"]
