from __future__ import annotations


class DuplicateKeyError(ValueError):
    def __init__(self, key: str, pointer: str) -> None:
        super().__init__(f"duplicate key {key!r} at {pointer or '/'}")
        self.key = key
        self.pointer = pointer
