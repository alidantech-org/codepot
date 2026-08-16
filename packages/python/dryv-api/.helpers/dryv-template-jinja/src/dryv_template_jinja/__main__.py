from __future__ import annotations

import argparse
import os

from .client import JinjaRenderClient


def main() -> int:
    parser = argparse.ArgumentParser(prog="dryv-template-jinja")
    parser.add_argument("--api", required=True, help="dryv-api renderer WebSocket URL")
    parser.add_argument("--connection-id", default=f"jinja-{os.getpid()}")
    args = parser.parse_args()
    JinjaRenderClient(max_concurrency=1).serve(args.api, connection_id=args.connection_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
