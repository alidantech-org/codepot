"""Presentation layer constants."""

from __future__ import annotations

# Language choices for interactive prompts
LANGUAGE_CHOICES = ["debug", "dart", "typescript"]

# Default file names
DEFAULT_INFERENCE_OUTPUT = "inference.json"

# Default boolean prompt values
DEFAULT_CONFIRM = False
DEFAULT_DRY_RUN = True
DEFAULT_USE_CUSTOM_TEMPLATES = False
DEFAULT_WRITE_OUTPUT = False

# Acronym replacements for table key formatting
ACRONYM_REPLACEMENTS = {
    "Api": "API",
    "Openapi": "OpenAPI",
    "Http": "HTTP",
    "Json": "JSON",
    "Yaml": "YAML",
    "Url": "URL",
    "Uri": "URI",
    "Id": "ID",
    "Dto": "DTO",
    "Sdk": "SDK",
}

# Tokens that indicate a numeric column for table formatting
NUMERIC_COLUMN_TOKENS = (
    "count",
    "total",
    "files",
    "operations",
    "schemas",
    "paths",
    "refs",
    "value",
)
