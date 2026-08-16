from __future__ import annotations

import hashlib
import importlib
import importlib.util
from pathlib import Path
from types import ModuleType

from .target import AuthorTarget


def load_module(target: AuthorTarget, *, project_root: Path | None = None) -> ModuleType:
    location = target.location
    candidate = Path(location)
    if not candidate.is_absolute() and project_root is not None:
        candidate = project_root / candidate
    if candidate.suffix == ".py" or candidate.exists():
        path = candidate.resolve()
        if not path.is_file():
            raise ValueError(f"author target file does not exist: {path}")
        digest = hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:12]
        module_name = f"_dryv_author_{digest}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ValueError(f"cannot load author module from {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return importlib.import_module(location)


__all__ = ["load_module"]
