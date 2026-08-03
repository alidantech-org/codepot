from pathlib import Path

from pipeline.pathing.config_loader import load_path_config
from pipeline.templates.package_loader import load_template_package_config


def test_typescript_template_package_config_loads() -> None:
    config = load_template_package_config(Path("templates/typescript/codepot.yaml"))

    assert config.name == "typescript"
    assert config.language.name == "typescript"
    assert config.language.extension == "ts"
    assert config.defaults.output == "generated/typescript"
    assert len(config.commands) == 5
    assert len(config.after_emit_hooks) == 3
    assert all(not hook.run_by_default for hook in config.after_emit_hooks)


def test_typescript_paths_config_loads_template_and_copy_groups() -> None:
    config = load_path_config(Path("templates/typescript/paths.yaml"))

    groups = {group.id: group for group in config.groups}

    assert len(config.groups) == 12
    assert groups["package_json"].template == "package.json.j2"
    assert groups["package_json"].copy is None
    assert groups["gitignore"].copy == ".gitignore"
    assert groups["gitignore"].template is None
    assert groups["operations"].output == "src/operations/{owner.name.path}/{item.name.path}.ts"
