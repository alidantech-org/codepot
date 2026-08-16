from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .result import AuthorResult


class AuthorProcessError(RuntimeError):
    def __init__(self, code: str, message: str, *, stderr: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.stderr = stderr


class AuthorProcess:
    def __init__(self, executable: str | None = None) -> None:
        self.executable = executable or sys.executable

    def compile(
        self,
        target: str,
        *,
        project_root: Path,
        representation: str = "json",
    ) -> AuthorResult:
        completed = subprocess.run(
            [
                self.executable,
                "-m",
                "dryv_author.host",
                target,
                "--project-root",
                str(project_root),
                "--representation",
                representation,
            ],
            cwd=project_root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
            encoding="utf-8",
        )
        try:
            document = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "dryv-author did not return its versioned JSON response",
                stderr=completed.stderr,
            ) from exc
        if not isinstance(document, dict) or document.get("protocol") != "dryv.author.host/v1":
            raise AuthorProcessError("CLI_AUTHOR_PROTOCOL", "dryv-author response protocol is unsupported")
        diagnostics_raw = document.get("diagnostics", [])
        if not isinstance(diagnostics_raw, list):
            raise AuthorProcessError("CLI_AUTHOR_PROTOCOL", "dryv-author diagnostics must be an array")
        diagnostics = tuple(dict(item) for item in diagnostics_raw if isinstance(item, dict))
        content = document.get("content")
        media_type = document.get("mediaType")
        result = AuthorResult(
            ok=bool(document.get("ok")),
            media_type=media_type if isinstance(media_type, str) else None,
            content=content.encode("utf-8") if isinstance(content, str) else None,
            diagnostics=diagnostics,
            ir_version=document.get("irVersion") if isinstance(document.get("irVersion"), str) else None,
            stderr=completed.stderr,
        )
        if completed.returncode not in {0, 1}:
            raise AuthorProcessError(
                "CLI_AUTHOR_PROCESS",
                f"dryv-author exited with code {completed.returncode}",
                stderr=completed.stderr,
            )
        return result


__all__ = ["AuthorProcess", "AuthorProcessError"]
