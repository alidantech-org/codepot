from __future__ import annotations

from pathlib import Path

import pytest

from core.errors import ConfigError
from archives.codepotg.src.codepot_file.models import CodepotTask
from archives.codepotg.src.codepot_file.runner import clean_task_paths
from archives.codepotg.src.emission.engine import emit
from archives.codepotg.src.emission.paths.config_loader import load_path_config
from archives.codepotg.tests.fixtures.contracts import make_template_contract


def test_existing_templates_without_write_policy_behave_as_before(tmp_path: Path) -> None:
    template_root = _write_templates(
        tmp_path / "templates",
        paths_yaml="""
folders:
  root:
    mode: once
    parts:
      - gen
""",
        files={"{root}/hello.txt.j2": "hello"},
    )

    result = emit(make_template_contract(tmp_path / "out", template_root))

    assert result.write_result.created == (tmp_path / "out" / "gen" / "hello.txt",)


def test_managed_files_create_and_update(tmp_path: Path) -> None:
    template_root = _write_policy_templates(
        tmp_path / "templates",
        files={"{root}/hello.txt.j2": "hello"},
    )
    output = tmp_path / "out"

    first = emit(make_template_contract(output, template_root))
    (template_root / "{root}" / "hello.txt.j2").write_text("hello changed", encoding="utf-8")
    second = emit(make_template_contract(output, template_root))

    assert first.write_result.created == (output / "gen" / "hello.txt",)
    assert second.write_result.updated == (output / "gen" / "hello.txt",)
    assert (output / "gen" / "hello.txt").read_text(encoding="utf-8") == "hello changed\n"


def test_immutable_file_creates_missing_and_skips_existing(tmp_path: Path) -> None:
    template_root = _write_policy_templates(
        tmp_path / "templates",
        files={"{module}/service.ts.j2": "first"},
    )
    output = tmp_path / "out"

    first = emit(make_template_contract(output, template_root))
    (template_root / "{module}" / "service.ts.j2").write_text("changed", encoding="utf-8")
    second = emit(make_template_contract(output, template_root))

    path = output / "src" / "modules" / "service.ts"
    assert first.write_result.immutable_created == (path,)
    assert second.write_result.immutable_skipped == (path,)
    assert path.read_text(encoding="utf-8") == "first\n"


def test_mode_once_behaves_like_immutable(tmp_path: Path) -> None:
    template_root = _write_templates(
        tmp_path / "templates",
        paths_yaml="""
write_policy:
  immutable_roots:
    - src
folders:
  module:
    mode: once
    parts:
      - src
      - modules
""",
        files={"{module}/service.ts.j2": "first"},
    )
    output = tmp_path / "out"

    emit(make_template_contract(output, template_root))
    (template_root / "{module}" / "service.ts.j2").write_text("changed", encoding="utf-8")
    second = emit(make_template_contract(output, template_root))

    assert second.write_result.immutable_skipped == (output / "src" / "modules" / "service.ts",)


def test_managed_write_under_protected_src_is_refused(tmp_path: Path) -> None:
    template_root = _write_templates(
        tmp_path / "templates",
        paths_yaml="""
write_policy:
  default_mode: managed
  managed_roots:
    - gen
  protected_roots:
    - src
folders:
  bad:
    mode: managed
    parts:
      - src
      - modules
""",
        files={"{bad}/controller.ts.j2": "bad"},
    )

    with pytest.raises(ConfigError, match="Unsafe template writes refused"):
        emit(make_template_contract(tmp_path / "out", template_root))


def test_managed_write_under_explicit_src_entities_is_allowed(tmp_path: Path) -> None:
    template_root = _write_policy_templates(
        tmp_path / "templates",
        files={"{entity}/entity.ts.j2": "entity"},
    )

    result = emit(make_template_contract(tmp_path / "out", template_root))

    assert (tmp_path / "out" / "src" / "entities" / "entity.ts") in result.write_result.created


def test_raw_files_inherit_folder_lifecycle(tmp_path: Path) -> None:
    template_root = _write_policy_templates(
        tmp_path / "templates",
        files={"{module}/raw.txt": "raw"},
    )
    output = tmp_path / "out"

    emit(make_template_contract(output, template_root))
    (template_root / "{module}" / "raw.txt").write_text("changed", encoding="utf-8")
    second = emit(make_template_contract(output, template_root))

    assert second.write_result.immutable_skipped == (output / "src" / "modules" / "raw.txt",)


def test_refresh_clean_uses_clean_roots_and_refuses_immutable(tmp_path: Path) -> None:
    template_root = _write_policy_templates(tmp_path / "templates", files={"{root}/x.txt.j2": "x"})
    policy = load_path_config(template_root).write_policy
    output = tmp_path / "out"
    gen = output / "gen"
    src = output / "src"
    gen.mkdir(parents=True)
    src.mkdir()

    clean_task_paths(
        _task(tmp_path, output, clean=(gen,)),
        config_root=tmp_path,
        write_policy=policy,
    )

    assert not gen.exists()
    with pytest.raises(ConfigError, match="Refusing to clean immutable path"):
        clean_task_paths(
            _task(tmp_path, output, clean=(src,)),
            config_root=tmp_path,
            write_policy=policy,
        )


def _write_policy_templates(root: Path, *, files: dict[str, str]) -> Path:
    return _write_templates(
        root,
        paths_yaml="""
write_policy:
  default_mode: managed
  managed_roots:
    - gen
    - src/entities
  immutable_roots:
    - src
  protected_roots:
    - src
  clean_roots:
    - gen
    - src/entities
folders:
  root:
    mode: managed
    parts:
      - gen
  module:
    mode: immutable
    parts:
      - src
      - modules
  entity:
    mode: managed
    parts:
      - src
      - entities
""",
        files=files,
    )


def _write_templates(root: Path, *, paths_yaml: str, files: dict[str, str]) -> Path:
    root.mkdir(parents=True)
    (root / "paths.yaml").write_text(paths_yaml.strip(), encoding="utf-8")
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def _task(tmp_path: Path, output: Path, *, clean: tuple[Path, ...]) -> CodepotTask:
    return CodepotTask(
        name="sdk",
        input=tmp_path / "openapi.yaml",
        language="debug",
        output=output,
        template_dir=tmp_path / "templates",
        clean=clean,
    )
