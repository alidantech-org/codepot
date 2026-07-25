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
class JsonlQueueLimits:
    max_records: int = 32
    max_pending_bytes: int = 32 * 1024 * 1024
    max_events: int = 256
    wait_timeout_seconds: float = 0.05


@dataclass(frozen=True, slots=True)
class JsonlQueueStats:
    record_high_water: int = 0
    pending_bytes_high_water: int = 0
    event_high_water: int = 0
    record_waits: int = 0
    event_waits: int = 0


@dataclass(frozen=True, slots=True)
class ExtractedRecord:
    section: str
    name: str
    raw: Any
    estimated_bytes: int = 0


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

    @classmethod
    def from_json(cls, value: Mapping[str, Any]) -> SectionManifest:
        return cls(
            file=str(value["file"]),
            count=int(value["count"]),
            bytes=int(value["bytes"]),
            sha256=str(value["sha256"]),
        )


@dataclass(frozen=True, slots=True)
class JsonlManifest:
    version: int
    source: Mapping[str, Any]
    root: Mapping[str, Any]
    sections: Mapping[str, SectionManifest]
    indexes: Mapping[str, Any]
    events: SectionManifest | None = None

    def to_json(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "version": self.version,
            "source": dict(self.source),
            "root": dict(self.root),
            "sections": {
                key: section.to_json() for key, section in sorted(self.sections.items())
            },
            "indexes": dict(self.indexes),
        }
        if self.events is not None:
            value["events"] = self.events.to_json()
        return value


@dataclass(slots=True)
class JsonlCompileResult:
    cache_dir: Path
    manifest: JsonlManifest
    hot_index: Any
    compatibility_path: Path | None = None
    reused: bool = False
    records_written: int = 0
    definitions_written: int = 0
    mentions_written: int = 0
    dependencies_written: int = 0
    queue_stats: JsonlQueueStats = field(default_factory=JsonlQueueStats)
    diagnostics: list[str] = field(default_factory=list)
