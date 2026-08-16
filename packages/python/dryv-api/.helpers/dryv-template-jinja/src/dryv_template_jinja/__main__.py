from __future__ import annotations

import json

from .client import JinjaRenderClient


def main() -> int:
    client = JinjaRenderClient()
    print(json.dumps({"renderer": client.hello.renderer_id, "version": client.hello.renderer_version, "capabilities": client.hello.capabilities, "fingerprint": client.hello.fingerprint}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
