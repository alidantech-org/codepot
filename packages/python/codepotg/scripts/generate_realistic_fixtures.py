"""Generate inspectable output from the realistic Nest, Next, and Dart fixture packs."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PACKAGE_ROOT / "src"
for value in (str(SOURCE_ROOT), str(PACKAGE_ROOT)):
    if value not in sys.path:
        sys.path.insert(0, value)

from app import GeneratorApp  # noqa: E402

FIXTURE_ROOT = PACKAGE_ROOT / "tests" / "fixtures" / "realistic_projects"
CANONICAL_OPENAPI = PACKAGE_ROOT / "tests" / "fixtures" / "openapi.json"
PACKS = {
    "nest_backend": "Codepotg.yml",
    "next_server_actions": "Codepotg.yml",
    "dart_client": "Codepotg.yaml",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate visible review output from realistic CodepotG fixture packs."
    )
    parser.add_argument("--pack", choices=("all", *PACKS), default="all")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    selected = PACKS if args.pack == "all" else {args.pack: PACKS[args.pack]}
    for pack, config_name in selected.items():
        project = FIXTURE_ROOT / pack
        generated_input = project / "openapi.generated.json"
        output = project / ".generated-review"
        cache = project / ".codepotg"
        if args.clean:
            shutil.rmtree(output, ignore_errors=True)
            shutil.rmtree(cache, ignore_errors=True)
            generated_input.unlink(missing_ok=True)

        _write_fictional_openapi(CANONICAL_OPENAPI, generated_input)
        result = GeneratorApp().generate(
            config_path=project / config_name,
            task_name="realistic",
        )
        task = result.tasks[0]
        print(
            f"{pack}: planned={len(task.planned)}, written={len(task.written)}, "
            f"updated={len(task.updated)}, unchanged={len(task.unchanged)}, "
            f"output={task.output_path}"
        )
    return 0


def _write_fictional_openapi(source: Path, destination: Path) -> None:
    raw = json.loads(source.read_text(encoding="utf-8"))
    sanitized = _sanitize(raw)
    if not isinstance(sanitized, dict):
        raise TypeError("OpenAPI fixture root must remain an object")
    info = sanitized.setdefault("info", {})
    if not isinstance(info, dict):
        raise TypeError("OpenAPI info must be an object")
    info.update(
        {
            "title": "Northstar Platform API",
            "description": (
                "Large fictional multi-tenant API used for CodepotG pack validation."
            ),
            "version": "v1",
        }
    )
    sanitized["servers"] = [
        {
            "url": "https://api.northstar.example/v1",
            "description": "Fictional production API",
        }
    ]
    destination.write_text(
        json.dumps(
            sanitized,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )


def _sanitize(value: Any) -> Any:
    if isinstance(value, str):
        return (
            value.replace("Alidantech", "Northstar")
            .replace("ALIDANTECH", "NORTHSTAR")
            .replace("alidantech", "northstar")
            .replace("Riderescue", "Sample Product")
            .replace("RideRescue", "Sample Product")
            .replace("riderescue", "sample-product")
            .replace("Sierre Technologies", "Example Technologies")
            .replace("Sierre", "Example")
            .replace("sierre", "example")
        )
    if isinstance(value, Mapping):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray)
    ):
        return [_sanitize(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
