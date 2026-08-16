from __future__ import annotations

import argparse
import json
import sys
from contextlib import redirect_stdout

from .compile import compile_target
from .contracts import HostCompileRequest


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m dryv_author.host")
    parser.add_argument("target")
    parser.add_argument("--project-root")
    parser.add_argument("--representation", choices=("json", "jsonl", "yaml"), default="json")
    args = parser.parse_args()

    # Author source is ordinary Python and may print. Reserve stdout exclusively for
    # the versioned host response so Project Clients can parse it deterministically.
    with redirect_stdout(sys.stderr):
        response = compile_target(
            HostCompileRequest(args.target, args.project_root, args.representation)
        )
    sys.stdout.write(json.dumps(response.to_document(), ensure_ascii=False, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if response.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
