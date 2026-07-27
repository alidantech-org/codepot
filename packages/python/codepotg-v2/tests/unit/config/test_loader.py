from pathlib import Path

import pytest

from codepotg.config import ConfigurationError, load_pack_manifest, load_project


def test_project_and_pack_documents_decode_strictly(tmp_path: Path) -> None:
    project_file = tmp_path / "codepotg.yaml"
    project_file.write_text(
        """
apiVersion: codepotg.dev/v2
name: example
sources:
  contract:
    adapter: ir
    file: contract.codepot.json
packs:
  sdk:
    source:
      local: packs/sdk
    input: contract
    output: generated
    options:
      mode: strict
""".strip(),
        encoding="utf-8",
    )
    pack_root = tmp_path / "packs" / "sdk"
    pack_root.mkdir(parents=True)
    (pack_root / "CodepotgPack.yaml").write_text(
        """
apiVersion: codepotg.dev/v2
id: example/sdk
version: 1.0.0
options:
  mode:
    default: strict
    choices: [strict, relaxed]
selections:
  schemas:
    select: groups.schemas.objects.each
    paths: [models]
""".strip(),
        encoding="utf-8",
    )

    project = load_project(project_file)
    manifest = load_pack_manifest(pack_root / "CodepotgPack.yaml")

    assert project.packs[0].input == "contract"
    assert dict(manifest.resolve_options(project.packs[0].options)) == {"mode": "strict"}
    assert manifest.selections[0].select == "groups.schemas.objects.each"


def test_duplicate_and_unknown_fields_are_rejected(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.yaml"
    duplicate.write_text(
        """
apiVersion: codepotg.dev/v2
name: first
name: second
sources: {}
packs: {}
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError, match="duplicate key"):
        load_project(duplicate)

    unknown = tmp_path / "unknown.yaml"
    unknown.write_text(
        """
apiVersion: codepotg.dev/v2
name: example
language: typescript
sources: {}
packs: {}
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError, match="unknown field"):
        load_project(unknown)
