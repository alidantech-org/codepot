from __future__ import annotations

from dataclasses import dataclass

HOST_PROTOCOL = "dryv.author.host/v1"


@dataclass(frozen=True, slots=True)
class HostCompileRequest:
    target: str
    project_root: str | None = None
    representation: str = "json"

    def __post_init__(self) -> None:
        if self.representation not in {"json", "jsonl", "yaml"}:
            raise ValueError("representation must be json, jsonl or yaml")


@dataclass(frozen=True, slots=True)
class HostCompileResponse:
    ok: bool
    media_type: str | None
    content: str | None
    diagnostics: tuple[dict[str, object], ...]
    ir_version: str

    def to_document(self) -> dict[str, object]:
        return {"protocol": HOST_PROTOCOL, "ok": self.ok, "mediaType": self.media_type, "content": self.content, "diagnostics": self.diagnostics, "irVersion": self.ir_version}


__all__ = ["HOST_PROTOCOL", "HostCompileRequest", "HostCompileResponse"]
