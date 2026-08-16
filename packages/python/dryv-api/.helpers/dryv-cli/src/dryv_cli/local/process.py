from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


class LocalProcessError(RuntimeError):
    def __init__(self, message: str, *, stderr: str = "") -> None:
        super().__init__(message)
        self.stderr = stderr


@dataclass(slots=True)
class OwnedProcess:
    argv: tuple[str, ...]
    cwd: Path | None = None
    process: subprocess.Popen[str] | None = None

    def start(self) -> None:
        if self.process is not None:
            raise RuntimeError("owned process is already started")
        self.process = subprocess.Popen(
            list(self.argv),
            cwd=self.cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            shell=False,
        )

    def require_running(self) -> None:
        if self.process is None:
            raise RuntimeError("owned process is not started")
        code = self.process.poll()
        if code is not None:
            stderr = self.process.stderr.read() if self.process.stderr is not None else ""
            raise LocalProcessError(f"child process exited with code {code}", stderr=stderr)

    def stop(self, *, timeout: float = 5.0) -> None:
        process = self.process
        if process is None:
            return
        self.process = None
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=timeout)
        if process.stderr is not None:
            process.stderr.close()


__all__ = ["LocalProcessError", "OwnedProcess"]
