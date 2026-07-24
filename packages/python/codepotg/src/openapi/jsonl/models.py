from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class JsonlLimits:
    max_root_items: int = 256
    max_root_bytes: int = 512 * 1024
    max_record_items: int = 250_000
    max_record_bytes: int = 16 * 1024 * 1024
    max_depth: int = 128


@dataclass(frozen=True, slots=True)
class HotIndexLimits:
    max_entries: int = 8_192
    max_bytes: int = 8 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class ExtractedRecord:
    section: str
    name: str
    raw: Any


@dataclass(frozen=True, slots=True)
class StreamSummary:
    root: Mapping[str, Any]
    source_size: int


@dataclass(frozen=True, slots=True)
class RecordLocation:
    section: str
    file: str
    offset: int
    length: int
    sha256: str
    key: str
    ref: str | None
    kind: str | None
    resources: tuple[str, ...] = ()
    pointer: str | None = None

    def to_json(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "section": self.section,
            "file": self.file,
            "offset": self.offset,
            "length": self.length,
            "sha256": self.sha256,
            "key": self.key,
            "ref": self.ref,
            "kind": self.kind,
            "resources": list(self.resources),
        }
        if self.pointer is not None:
            value["pointer"] = self.pointer
        return value

    @classmethod
    def from_json(cls, value: Mapping[str, Any]) -> RecordLocation:
        return cls(
            section=str(value["section"]),
            file=str(value["file"]),
            offset=int(value["offset"]),
            length=int(value["length"]),
            sha256=str(value["sha256"]),
            key=str(value["key"]),
            ref=str(value["ref"]) if value.get("ref") is not None else None,
            kind=str(value["kind"]) if value.get("kind") is not None else None,
            resources=tuple(str(item) for item in value.get("resources", ())),
            pointer=str(value["pointer"]) if value.get("pointer") is not None else None,
        )


@dataclass(frozen=True, slots=True)
class SectionManifest:
    file: str
    count: int
    bytes: int
    sha256: str

    def to_json(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "count": self.count,
            "bytes": self.bytes,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class JsonlManifest:
    version: int
    source: Mapping[str, Any]
    root: Mapping[str, Any]
    sections: Mapping[str, SectionManifest]
    indexes: Mapping[str, Any]

    def to_json(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "source": dict(self.source),
            "root": dict(self.root),
            "sections": {
                key: value.to_json() for key, value in sorted(self.sections.items())
            },
            "indexes": dict(self.indexes),
        }


@dataclass(slots=True)
class JsonlCompileResult:
    cache_dir: Path
    manifest: JsonlManifest
    hot_index: Any
    reused: bool = False
    records_written: int = 0
    definitions_written: int = 0
    mentions_written: int = 0
    dependencies_written: int = 0
    diagnostics: list[str] = field(default_factory=list)
