from __future__ import annotations

from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment


def create_environment() -> SandboxedEnvironment:
    environment = SandboxedEnvironment(
        autoescape=False,
        undefined=StrictUndefined,
        enable_async=False,
        keep_trailing_newline=True,
    )
    environment.globals.clear()
    return environment


__all__ = ["create_environment"]
