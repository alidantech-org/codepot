from pathlib import Path

import pytest

from codepotg.generation import GeneratedArtifact, MemoryOutput
from codepotg.infrastructure import ManagedFilesystemWriter, ManagedWriteKind


def _output(*items: tuple[str, bytes]) -> MemoryOutput:
    return MemoryOutput(
        tuple(
            sorted(
                (
                    GeneratedArtifact(
                        id=path,
                        path=path,
                        content=content,
                        target_id=None,
                        template_id=path,
                    )
                    for path, content in items
                ),
                key=lambda item: item.path,
            )
        )
    )


def test_managed_writer_tracks_changes_and_deletes_unchanged_stale_files(
    tmp_path: Path,
) -> None:
    writer = ManagedFilesystemWriter()
    first = writer.write(
        _output(("generated/a.txt", b"a"), ("generated/b.txt", b"b")),
        tmp_path,
    )
    second = writer.write(
        _output(("generated/a.txt", b"changed")),
        tmp_path,
    )

    assert tuple(item.kind for item in first.changes) == (
        ManagedWriteKind.CREATE,
        ManagedWriteKind.CREATE,
    )
    assert {item.path: item.kind for item in second.changes} == {
        "generated/a.txt": ManagedWriteKind.CHANGE,
        "generated/b.txt": ManagedWriteKind.DELETE,
    }
    assert not (tmp_path / "generated" / "b.txt").exists()
    assert (tmp_path / ".codepotg" / "generation-state.json").is_file()


def test_managed_writer_refuses_unmanaged_collisions_and_manual_edits(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "generated" / "a.txt"
    destination.parent.mkdir(parents=True)
    destination.write_text("manual", encoding="utf-8")
    writer = ManagedFilesystemWriter()

    with pytest.raises(ValueError, match="WRITE_UNMANAGED_COLLISION"):
        writer.write(_output(("generated/a.txt", b"generated")), tmp_path)

    destination.unlink()
    writer.write(_output(("generated/a.txt", b"generated")), tmp_path)
    destination.write_text("edited", encoding="utf-8")
    with pytest.raises(ValueError, match="WRITE_PROTECTED_MODIFICATION"):
        writer.write(_output(("generated/a.txt", b"next")), tmp_path)
