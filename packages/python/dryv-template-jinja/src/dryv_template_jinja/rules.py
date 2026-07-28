from __future__ import annotations

from dataclasses import dataclass, fields

_ALLOWED_NEWLINES = ("\n", "\r", "\r\n")


@dataclass(frozen=True, slots=True)
class JinjaEngineRules:
    """Host-controlled immutable behavior and resource limits."""

    trim_blocks: bool = True
    lstrip_blocks: bool = True
    keep_trailing_newline: bool = True
    newline_sequence: str = "\n"

    max_template_id_length: int = 512
    max_template_bytes: int = 1_000_000
    max_partial_count: int = 1_000
    max_partial_bytes: int = 5_000_000
    max_context_depth: int = 64
    max_context_items: int = 100_000
    max_include_depth: int = 32
    max_render_bytes: int = 5_000_000
    max_ast_nodes: int = 100_000

    cache_entries: int = 256

    def __post_init__(self) -> None:
        if self.newline_sequence not in _ALLOWED_NEWLINES:
            raise ValueError("newline_sequence must be one of '\\n', '\\r', or '\\r\\n'")
        for item in fields(self):
            if item.name in {
                "trim_blocks",
                "lstrip_blocks",
                "keep_trailing_newline",
                "newline_sequence",
            }:
                continue
            value = getattr(self, item.name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{item.name} must be a positive integer")

    def identity(self) -> tuple[tuple[str, object], ...]:
        return tuple((item.name, getattr(self, item.name)) for item in fields(self))
