"""Schema linking behavior for generated and edited CodepotG configs."""

from __future__ import annotations

from pathlib import Path

from codepot_file.editor import (
    TaskDraft,
    add_task_to_codepotg_config,
    init_codepotg_config,
    starter_draft,
)
from codepot_file.loader import load_codepotg_config
from codepotg.schemas import CODEPOTG_SCHEMA_ID


def test_init_writes_language_server_and_typed_schema_links(tmp_path: Path) -> None:
    config = init_codepotg_config(root=tmp_path, draft=starter_draft())
    content = config.read_text(encoding="utf-8")
    loaded = load_codepotg_config(config)

    assert content.startswith(
        f"# yaml-language-server: $schema={CODEPOTG_SCHEMA_ID}\n"
    )
    assert f"$schema: {CODEPOTG_SCHEMA_ID}" in content
    assert loaded.schema_uri == CODEPOTG_SCHEMA_ID


def test_add_task_preserves_schema_links(tmp_path: Path) -> None:
    config = init_codepotg_config(root=tmp_path, draft=starter_draft())

    add_task_to_codepotg_config(
        config_path=config,
        draft=TaskDraft(
            name="java-client",
            input="./openapi.yaml",
            language="java",
            output="./generated/java",
        ),
    )

    content = config.read_text(encoding="utf-8")
    loaded = load_codepotg_config(config)
    assert content.count("yaml-language-server: $schema=") == 1
    assert content.count("$schema:") == 2  # modeline plus YAML field
    assert loaded.schema_uri == CODEPOTG_SCHEMA_ID
    assert {task.name for task in loaded.tasks} == {"sdk", "java-client"}
