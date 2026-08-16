from __future__ import annotations

from pathlib import Path, PurePosixPath

MANAGED_STATE_PATH = ".dryv/managed-outputs.json"


class FilesystemError(RuntimeError):
    def __init__(self, code: str, message: str, *, path: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path


def safe_project_path(root: Path, relative_path: str, *, internal: bool = False) -> Path:
    root = root.resolve()
    if not relative_path or relative_path.startswith("/") or "\\" in relative_path:
        raise FilesystemError("CLI_FS_PATH", f"unsafe project-relative path {relative_path!r}", path=relative_path)
    relative = PurePosixPath(relative_path)
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise FilesystemError("CLI_FS_PATH", f"unsafe project-relative path {relative_path!r}", path=relative_path)
    first = relative.parts[0]
    if len(first) >= 2 and first[1] == ":":
        raise FilesystemError("CLI_FS_PATH", f"drive-qualified path is forbidden: {relative_path!r}", path=relative_path)
    if not internal and first == ".dryv":
        raise FilesystemError("CLI_FS_RESERVED", "generated artifacts cannot write inside the reserved .dryv directory", path=relative_path)
    target = root.joinpath(*relative.parts)
    resolved = target.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise FilesystemError("CLI_FS_ESCAPE", f"path escapes project root: {relative_path!r}", path=relative_path) from exc
    return target


__all__ = ["FilesystemError", "MANAGED_STATE_PATH", "safe_project_path"]
