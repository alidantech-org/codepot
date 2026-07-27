from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

from codepotg.generation import MemoryOutput


@dataclass(frozen=True, slots=True)
class ArchiveResult:
    path: str | None
    content: bytes
    entries: tuple[str, ...]


class ZipArchiveWriter:
    """Create deterministic ZIP archives from already validated memory output."""

    def build(self, output: MemoryOutput) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(
            buffer,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for artifact in output.artifacts:
                info = zipfile.ZipInfo(artifact.path, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                info.create_system = 3
                archive.writestr(info, artifact.content)
        return buffer.getvalue()

    def write(self, output: MemoryOutput, destination: str | Path) -> ArchiveResult:
        path = Path(destination).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        content = self.build(output)
        temporary = path.with_name(f".{path.name}.codepotg.tmp")
        try:
            temporary.write_bytes(content)
            temporary.replace(path)
        finally:
            if temporary.exists():
                temporary.unlink()
        return ArchiveResult(
            path=str(path),
            content=content,
            entries=tuple(item.path for item in output.artifacts),
        )
