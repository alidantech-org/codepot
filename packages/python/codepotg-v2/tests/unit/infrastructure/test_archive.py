import io
import zipfile

from codepotg.generation import GeneratedArtifact, MemoryOutput
from codepotg.infrastructure import ZipArchiveWriter


def _output() -> MemoryOutput:
    return MemoryOutput(
        (
            GeneratedArtifact(
                id="a",
                path="a.txt",
                content=b"a\n",
                target_id=None,
                template_id="a.txt",
            ),
            GeneratedArtifact(
                id="b",
                path="nested/b.txt",
                content=b"b\n",
                target_id=None,
                template_id="nested/b.txt",
            ),
        )
    )


def test_zip_archive_is_deterministic_and_preserves_exact_paths() -> None:
    writer = ZipArchiveWriter()
    first = writer.build(_output())
    second = writer.build(_output())
    assert first == second

    with zipfile.ZipFile(io.BytesIO(first)) as archive:
        assert archive.namelist() == ["a.txt", "nested/b.txt"]
        assert archive.read("nested/b.txt") == b"b\n"
