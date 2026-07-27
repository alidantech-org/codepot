from __future__ import annotations


class RenderLimitError(ValueError):
    def __init__(self, actual_bytes: int, max_bytes: int) -> None:
        super().__init__("rendered output exceeds the configured byte limit")
        self.actual_bytes = actual_bytes
        self.max_bytes = max_bytes


class OutputAccumulator:
    def __init__(self, max_bytes: int) -> None:
        self._max_bytes = max_bytes
        self._bytes = 0
        self._chunks: list[str] = []

    @property
    def byte_count(self) -> int:
        return self._bytes

    def append(self, chunk: str) -> None:
        encoded = chunk.encode("utf-8", errors="strict")
        next_size = self._bytes + len(encoded)
        if next_size > self._max_bytes:
            raise RenderLimitError(next_size, self._max_bytes)
        self._chunks.append(chunk)
        self._bytes = next_size

    def content(self) -> str:
        return "".join(self._chunks)
