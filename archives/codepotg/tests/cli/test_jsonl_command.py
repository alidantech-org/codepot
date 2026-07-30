from __future__ import annotations

import json
from contextlib import chdir
from pathlib import Path

from typer.testing import CliRunner

from archives.codepotg.cli.main import app


def test_jsonl_command_writes_visible_cache_and_progress(tmp_path: Path) -> None:
    source = tmp_path / "openapi.json"
    source.write_text(
        json.dumps(
            {
                "openapi": "3.1.0",
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {
                    "/users": {
                        "get": {
                            "operationId": "listUsers",
                            "responses": {"200": {"description": "OK"}},
                        }
                    }
                },
                "components": {
                    "schemas": {
                        "User": {
                            "type": "object",
                            "properties": {"id": {"type": "string"}},
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    runner = CliRunner()

    with chdir(tmp_path):
        result = runner.invoke(
            app,
            ["jsonl", "openapi.json", "--output", ".cache/openapi", "--verbose"],
        )

    assert result.exit_code == 0, result.output
    assert "Compiling OpenAPI into indexed JSONL" in result.output
    assert "Writing JSONL:" not in result.output
    assert "Wrote JSONL:" in result.output
    assert "SQLite index:" in result.output
    assert "JSONL cache ready" in result.output
    assert "paths.jsonl" in result.output
    assert "components/schemas.jsonl" in result.output
    assert "index.sqlite" in result.output
    assert (tmp_path / ".cache/openapi/manifest.json").is_file()
    assert (tmp_path / ".cache/openapi/paths.jsonl").is_file()
    assert (tmp_path / ".cache/openapi/components/schemas.jsonl").is_file()
    assert (tmp_path / ".cache/openapi/index.sqlite").is_file()
    assert (tmp_path / ".cache/openapi/events.jsonl").is_file()


def test_jsonl_command_reuses_unchanged_cache(tmp_path: Path) -> None:
    source = tmp_path / "openapi.json"
    source.write_text(
        json.dumps(
            {
                "openapi": "3.1.0",
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {},
            }
        ),
        encoding="utf-8",
    )
    runner = CliRunner()

    with chdir(tmp_path):
        first = runner.invoke(app, ["jsonl", "openapi.json"])
        second = runner.invoke(app, ["jsonl", "openapi.json"])

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    assert "Reused JSONL cache" in second.output
