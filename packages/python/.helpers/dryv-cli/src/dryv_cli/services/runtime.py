from __future__ import annotations

from dryv import DryvRuntime, create_runtime


def load_runtime() -> DryvRuntime:
    return create_runtime()
