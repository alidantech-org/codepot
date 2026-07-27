from pathlib import Path

import pytest

from codepotg.generation import GeneratedArtifact, MemoryOutput
from codepotg.infrastructure import TransactionalFilesystemWriter, WriteKind


def _output(content: bytes = b"new\n") -> MemoryOutput:
    return MemoryOutput(
        (
            GeneratedArtifact(
                id="artifact",
                path="generated/file.txt",
                content=content,
                target_id=None,
                template_id="file.txt",
            ),
        )
    )


def test_transactional_writer_creates_changes_and_leaves_exact_files(tmp_path: Path) -> None:
    writer = TransactionalFilesystemWriter()
    first = writer.write(_output(), tmp_path)
    second = writer.write(_output(), tmp_path)
    third = writer.write(_output(b"changed\n"), tmp_path)

    assert first.changes[0].kind is WriteKind.CREATE
    assert second.changes[0].kind is WriteKind.LEAVE
    assert third.changes[0].kind is WriteKind.CHANGE
    assert (tmp_path / "generated" / "file.txt").read_bytes() == b"changed\n"


def test_writer_rejects_traversal_without_touching_destination(tmp_path: Path) -> None:
    output = MemoryOutput(
        (
            GeneratedArtifact(
                id="bad",
                path="../escape.txt",
                content=b"unsafe",
                target_id=None,
                template_id="bad",
            ),
        )
    )
    with pytest.raises(ValueError, match="traversal"):
        TransactionalFilesystemWriter().write(output, tmp_path)
    assert not (tmp_path.parent / "escape.txt").exists()
