from __future__ import annotations


class JsonlCompilerError(RuntimeError):
    """Base error for JSONL extraction, indexing, and lookup."""


class JsonlInputError(JsonlCompilerError):
    """Raised when the input is unsupported or not a valid OpenAPI JSON document."""


class JsonlLimitError(JsonlCompilerError):
    """Raised when a bounded root value or record exceeds configured limits."""


class JsonlQueueError(JsonlCompilerError):
    """Raised when a bounded compiler or event queue worker fails."""


class JsonlLookupError(JsonlCompilerError):
    """Raised when an indexed record cannot be read or verified."""
