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
    def __init__(self, executable: str | None = None, *, timeout: float = 120.0) -> None:
        if timeout <= 0:
            raise ValueError("Author process timeout must be positive")
        self.executable = executable or sys.executable
        self.timeout = timeout

    def compile(
        self,
        target: str,
        *,
        project_root: Path,
        representation: str = "json",
    ) -> AuthorResult:
        try:
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
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            raise AuthorProcessError(
                "CLI_AUTHOR_TIMEOUT",
                f"dryv-author exceeded the {self.timeout:g}s process timeout",
                stderr=stderr,
            ) from exc
        except OSError as exc:
            raise AuthorProcessError(
                "CLI_AUTHOR_START",
                f"could not start dryv-author: {exc}",
            ) from exc

        try:
            document = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "dryv-author did not return its versioned JSON response",
                stderr=completed.stderr,
            ) from exc
        if not isinstance(document, dict) or document.get("protocol") != "dryv.author.host/v1":
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "dryv-author response protocol is unsupported",
                stderr=completed.stderr,
            )
        ok = document.get("ok")
        if not isinstance(ok, bool):
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "dryv-author response ok must be a boolean",
                stderr=completed.stderr,
            )
        diagnostics_raw = document.get("diagnostics", [])
        if not isinstance(diagnostics_raw, list) or not all(
            isinstance(item, dict) and all(isinstance(key, str) for key in item)
            for item in diagnostics_raw
        ):
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "dryv-author diagnostics must be an array of JSON objects",
                stderr=completed.stderr,
            )
        content = document.get("content")
        media_type = document.get("mediaType")
        ir_version = document.get("irVersion")
        if content is not None and not isinstance(content, str):
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "dryv-author response content must be a string or null",
                stderr=completed.stderr,
            )
        if media_type is not None and not isinstance(media_type, str):
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "dryv-author response mediaType must be a string or null",
                stderr=completed.stderr,
            )
        if not isinstance(ir_version, str) or not ir_version:
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "dryv-author response requires irVersion",
                stderr=completed.stderr,
            )
        if ok and (content is None or media_type is None):
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "successful dryv-author response requires content and mediaType",
                stderr=completed.stderr,
            )
        if not ok and content is not None:
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "failed dryv-author response must not include Canonical IR content",
                stderr=completed.stderr,
            )

        result = AuthorResult(
            ok=ok,
            media_type=media_type,
            content=content.encode("utf-8") if content is not None else None,
            diagnostics=tuple(dict(item) for item in diagnostics_raw),
            ir_version=ir_version,
            stderr=completed.stderr,
        )
        if completed.returncode not in {0, 1}:
            raise AuthorProcessError(
                "CLI_AUTHOR_PROCESS",
                f"dryv-author exited with code {completed.returncode}",
                stderr=completed.stderr,
            )
        if (completed.returncode == 0) != ok:
            raise AuthorProcessError(
                "CLI_AUTHOR_PROTOCOL",
                "dryv-author exit status disagrees with its response",
                stderr=completed.stderr,
            )
        return result


__all__ = ["AuthorProcess", "AuthorProcessError"]
