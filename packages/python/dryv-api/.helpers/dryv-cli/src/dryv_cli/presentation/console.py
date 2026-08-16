from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TextIO


@dataclass(slots=True)
class Console:
    stdout: TextIO = sys.stdout
    stderr: TextIO = sys.stderr

    def write(self, message: str = "") -> None:
        self.stdout.write(message + "\n")
        self.stdout.flush()

    def error(self, message: str) -> None:
        self.stderr.write(message + "\n")
        self.stderr.flush()


__all__ = ["Console"]
