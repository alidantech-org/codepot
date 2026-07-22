from __future__ import annotations

import json
from constants.files import ENCODING_UTF8, EXT_JSON, EXT_YAML, EXT_YML
from constants.openapi import (
    ERR_FILE_NOT_FOUND,
    ERR_LOAD_FAILED,
    ERR_MISSING_OPENAPI,
    ERR_MISSING_PATHS,
    ERR_NOT_A_FILE,
    ERR_ROOT_NOT_OBJECT,
    ERR_UNSUPPORTED_EXTENSION,
    OPENAPI,
    PATHS,
)
from pathlib import Path
from typing import Any

import yaml

from core.errors import OpenApiLoadError
from openapi.document import OpenApiDocument


def load_openapi_document(path: str | Path) -> OpenApiDocument:
    path = Path(path)

    if not path.exists():
        raise OpenApiLoadError(ERR_FILE_NOT_FOUND.format(path=path))

    if not path.is_file():
        raise OpenApiLoadError(ERR_NOT_A_FILE.format(path=path))

    suffix = path.suffix.lower()

    try:
        if suffix in {EXT_YAML, EXT_YML}:
            raw = _load_yaml(path)
        elif suffix == EXT_JSON:
            raw = _load_json(path)
        else:
            raise OpenApiLoadError(ERR_UNSUPPORTED_EXTENSION.format(suffix=suffix))
    except OpenApiLoadError:
        raise
    except Exception as exc:
        raise OpenApiLoadError(ERR_LOAD_FAILED.format(path=path)) from exc

    if not isinstance(raw, dict):
        raise OpenApiLoadError(ERR_ROOT_NOT_OBJECT)

    if OPENAPI not in raw:
        raise OpenApiLoadError(ERR_MISSING_OPENAPI)

    if PATHS not in raw:
        raise OpenApiLoadError(ERR_MISSING_PATHS)

    return OpenApiDocument(path=path, raw=raw)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding=ENCODING_UTF8) as file:
        value = yaml.safe_load(file)

    return value or {}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding=ENCODING_UTF8) as file:
        value = json.load(file)

    return value or {}
