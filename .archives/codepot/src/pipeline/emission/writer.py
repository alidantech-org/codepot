"""Rendered file writing helpers."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from archives.codepot.src.pipeline.emission.renderer import RenderedFile, RenderedFiles


class FileWriteStatus(StrEnum):
    """File write result status."""

    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    WOULD_CREATE = "would_create"
    WOULD_UPDATE = "would_update"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class FileWriteResult:
    """Result for one rendered file write."""

    file_id: str
    output_path: Path
    relative_output_path: str
    status: FileWriteStatus


@dataclass(frozen=True)
class FileWriteResults:
    """All rendered file write results."""

    files: tuple[FileWriteResult, ...]

    @property
    def created(self) -> int:
        """Return created file count."""

        return sum(1 for file in self.files if file.status == FileWriteStatus.CREATED)

    @property
    def updated(self) -> int:
        """Return updated file count."""

        return sum(1 for file in self.files if file.status == FileWriteStatus.UPDATED)

    @property
    def unchanged(self) -> int:
        """Return unchanged file count."""

        return sum(1 for file in self.files if file.status == FileWriteStatus.UNCHANGED)

    @property
    def would_create(self) -> int:
        """Return dry-run would-create count."""

        return sum(
            1 for file in self.files if file.status == FileWriteStatus.WOULD_CREATE
        )

    @property
    def would_update(self) -> int:
        """Return dry-run would-update count."""

        return sum(
            1 for file in self.files if file.status == FileWriteStatus.WOULD_UPDATE
        )

    @property
    def skipped(self) -> int:
        """Return skipped file count."""

        return sum(
            1 for file in self.files if file.status == FileWriteStatus.SKIPPED
        )


def _existing_content(path: Path) -> str | None:
    """Read existing content when file exists."""

    if not path.exists():
        return None

    if not path.is_file():
        raise ValueError(f"Output path exists but is not a file: {path}")

    return path.read_text(encoding="utf-8")


def _existing_bytes(path: Path) -> bytes | None:
    """Read existing bytes when file exists."""

    if not path.exists():
        return None

    if not path.is_file():
        raise ValueError(f"Output path exists but is not a file: {path}")

    return path.read_bytes()


def _static_source_bytes(file: RenderedFile) -> bytes:
    """Read source bytes for a static file."""

    if file.source_path is None:
        raise ValueError(f"Static file has no source path: {file.file_id}")

    return file.source_path.read_bytes()


def _status_for_static_file(
    *,
    file: RenderedFile,
    dry_run: bool,
) -> FileWriteStatus:
    """Determine write status for one static copied file."""

    source_bytes = _static_source_bytes(file)
    existing = _existing_bytes(file.output_path)

    if existing is None:
        return FileWriteStatus.WOULD_CREATE if dry_run else FileWriteStatus.CREATED

    if existing == source_bytes:
        return FileWriteStatus.UNCHANGED

    return FileWriteStatus.WOULD_UPDATE if dry_run else FileWriteStatus.UPDATED


def _status_for_rendered_file(
    *,
    file: RenderedFile,
    dry_run: bool,
) -> FileWriteStatus:
    """Determine write status for one rendered text file."""

    existing = _existing_content(file.output_path)

    if existing is None:
        return FileWriteStatus.WOULD_CREATE if dry_run else FileWriteStatus.CREATED

    if existing == file.content:
        return FileWriteStatus.UNCHANGED

    return FileWriteStatus.WOULD_UPDATE if dry_run else FileWriteStatus.UPDATED


def _status_for_file(
    *,
    file: RenderedFile,
    dry_run: bool,
) -> FileWriteStatus:
    """Determine write status for one output file."""

    if file.is_static:
        return _status_for_static_file(file=file, dry_run=dry_run)

    return _status_for_rendered_file(file=file, dry_run=dry_run)


def _write_static_file(file: RenderedFile) -> None:
    """Copy one static file to disk."""

    if file.source_path is None:
        raise ValueError(f"Static file has no source path: {file.file_id}")

    file.output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(file.source_path, file.output_path)


def _write_rendered_file(file: RenderedFile) -> None:
    """Write one rendered text file to disk."""

    file.output_path.parent.mkdir(parents=True, exist_ok=True)
    file.output_path.write_text(file.content, encoding="utf-8")


def _write_file(file: RenderedFile) -> None:
    """Write one output file to disk."""

    if file.is_static:
        _write_static_file(file)
        return

    _write_rendered_file(file)


def write_rendered_file(
    *,
    file: RenderedFile,
    dry_run: bool,
) -> FileWriteResult:
    """Write one rendered/static file or return dry-run status."""

    status = _status_for_file(file=file, dry_run=dry_run)

    if not dry_run and status in {FileWriteStatus.CREATED, FileWriteStatus.UPDATED}:
        _write_file(file)

    return FileWriteResult(
        file_id=file.file_id,
        output_path=file.output_path,
        relative_output_path=file.relative_output_path,
        status=status,
    )


def write_rendered_files(
    *,
    rendered: RenderedFiles,
    dry_run: bool,
) -> FileWriteResults:
    """Write all rendered/static files."""

    return FileWriteResults(
        files=tuple(
            write_rendered_file(
                file=file,
                dry_run=dry_run,
            )
            for file in rendered.files
        )
    )