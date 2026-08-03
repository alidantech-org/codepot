"""Load and validate CodepotG YAML configuration files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from archives.codepotg.src.codepot_file.models import CodepotCommand, CodepotFile, CodepotTask
from archives.codepotg.src.core.errors import ConfigError

CODEPOTG_CONFIG_YAML = "Codepotg.yaml"
CODEPOTG_CONFIG_YML = "Codepotg.yml"
CODEPOTG_CONFIG_NAME = CODEPOTG_CONFIG_YAML
SUPPORTED_CONFIG_NAMES = (CODEPOTG_CONFIG_YAML, CODEPOTG_CONFIG_YML)
LEGACY_CONFIG_NAMES = ("CodepotFile.yml", "CodepotFile.yaml")
SCHEMA_KEY = "$schema"


def resolve_codepotg_config(config_path: Path | None = None) -> Path:
    """Resolve an explicit config or discover a project-local CodepotG config."""
    if config_path is not None:
        path = config_path.expanduser().resolve()
        _reject_legacy_name(path)
        if not path.exists():
            raise ConfigError(f"CodepotG config not found: {path}")
        if not path.is_file():
            raise ConfigError(f"CodepotG config path is not a file: {path}")
        return path

    current = Path.cwd()
    found = [current / name for name in SUPPORTED_CONFIG_NAMES if (current / name).exists()]
    if len(found) > 1:
        names = ", ".join(path.name for path in found)
        raise ConfigError(
            f"Multiple CodepotG configs found ({names}). "
            "Keep only one or pass an explicit --config path."
        )
    if found:
        path = found[0]
        if not path.is_file():
            raise ConfigError(f"CodepotG config path is not a file: {path}")
        return path.resolve()

    legacy = [current / name for name in LEGACY_CONFIG_NAMES if (current / name).exists()]
    if legacy:
        names = ", ".join(path.name for path in legacy)
        raise ConfigError(
            f"Legacy Codepot config detected ({names}).\n"
            f"CodepotG uses {CODEPOTG_CONFIG_YAML} or {CODEPOTG_CONFIG_YML}; "
            "rename or recreate the Python generator config."
        )

    raise ConfigError(
        f"{CODEPOTG_CONFIG_YAML} or {CODEPOTG_CONFIG_YML} not found.\n"
        "Add one CodepotG config with allow: true before running generation in this directory."
    )


def load_codepotg_config(config_path: Path | None = None) -> CodepotFile:
    """Load and validate a CodepotG configuration."""
    path = resolve_codepotg_config(config_path)
    root = path.parent
    raw = load_codepotg_yaml(path)

    allow = raw.get("allow") is True
    defaults_raw = raw.get("defaults") or {}
    if not isinstance(defaults_raw, dict):
        raise ConfigError("CodepotG config defaults must be an object.")

    tasks_raw = raw.get("tasks")
    if not isinstance(tasks_raw, dict) or not tasks_raw:
        raise ConfigError("CodepotG config must define a non-empty tasks object.")

    tasks = tuple(
        _task_from_yaml(
            name=str(name),
            raw=_merge_defaults(defaults_raw, value),
            root=root,
        )
        for name, value in tasks_raw.items()
    )

    return CodepotFile(
        path=path,
        root=root,
        allow=allow,
        defaults=dict(defaults_raw),
        tasks=tasks,
        schema_uri=_optional_schema_uri(raw.get(SCHEMA_KEY)),
    )


def load_codepotg_yaml(path: Path) -> dict[str, Any]:
    """Read a CodepotG YAML object without resolving tasks."""
    _reject_legacy_name(path)
    with path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}

    if not isinstance(raw, dict):
        raise ConfigError("CodepotG config root must be an object.")
    _optional_schema_uri(raw.get(SCHEMA_KEY))
    return raw


def _merge_defaults(defaults: dict[str, Any], task_raw: Any) -> dict[str, Any]:
    if not isinstance(task_raw, dict):
        return task_raw
    merged = dict(defaults)
    merged.update(task_raw)
    return merged


def _task_from_yaml(name: str, raw: Any, root: Path) -> CodepotTask:
    if not isinstance(raw, dict):
        raise ConfigError(f"Task '{name}' must be an object.")

    input_path = _required_path(raw, "input", name, root)
    output_path = _required_path(raw, "output", name, root)
    language = raw.get("language")
    if not isinstance(language, str) or not language.strip():
        raise ConfigError(f"Task '{name}' must define language.")

    template_dir = _optional_template_path(raw, name=name, root=root)

    return CodepotTask(
        name=name,
        input=input_path,
        language=language.strip(),
        output=output_path,
        template_dir=template_dir,
        clean=_paths(raw.get("clean", ()), root, task_name=name, field_name="clean"),
        before=_commands(raw.get("before", ()), root, task_name=name, field_name="before"),
        after=_commands(raw.get("after", ()), root, task_name=name, field_name="after"),
        env=_env(raw.get("env"), task_name=name, field_name="env"),
        description=str(raw.get("description", "") or ""),
        frontend=_frontend(raw.get("frontend"), task_name=name),
    )


def _optional_template_path(raw: dict[str, Any], *, name: str, root: Path) -> Path | None:
    template_value = raw.get("templateDir", raw.get("templates"))
    if template_value in (None, ""):
        return None
    if not isinstance(template_value, str) or not template_value.strip():
        raise ConfigError(f"Task '{name}' field templateDir/templates must be a path string.")
    return _resolve_path(root, template_value)


def _frontend(raw: Any, *, task_name: str) -> str | None:
    if raw in (None, ""):
        return None
    if not isinstance(raw, str) or not raw.strip():
        raise ConfigError(f"Task '{task_name}' field frontend must be a string.")
    return raw.strip()


def _required_path(raw: dict[str, Any], field_name: str, task_name: str, root: Path) -> Path:
    value = raw.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"Task '{task_name}' must define {field_name}.")
    return _resolve_path(root, value)


def _paths(raw: Any, root: Path, *, task_name: str, field_name: str) -> tuple[Path, ...]:
    if raw in (None, ""):
        return ()
    if not isinstance(raw, list | tuple):
        raise ConfigError(f"Task '{task_name}' field {field_name} must be a list.")

    paths: list[Path] = []
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            raise ConfigError(f"Task '{task_name}' field {field_name} must contain paths.")
        paths.append(_resolve_path(root, item))
    return tuple(paths)


def _commands(
    raw: Any,
    root: Path,
    *,
    task_name: str,
    field_name: str,
) -> tuple[CodepotCommand, ...]:
    if raw in (None, ""):
        return ()
    if not isinstance(raw, list | tuple):
        raise ConfigError(f"Task '{task_name}' field {field_name} must be a list.")

    commands: list[CodepotCommand] = []
    for index, item in enumerate(raw, start=1):
        if isinstance(item, str):
            commands.append(CodepotCommand(name=None, run=item))
            continue
        if not isinstance(item, dict):
            raise ConfigError(
                f"Task '{task_name}' command {field_name}[{index}] must be an object."
            )

        run = item.get("run")
        if not isinstance(run, str) or not run.strip():
            raise ConfigError(f"Task '{task_name}' command {field_name}[{index}] must define run.")
        cwd = item.get("cwd")
        commands.append(
            CodepotCommand(
                name=str(item["name"]) if item.get("name") is not None else None,
                run=run,
                cwd=_resolve_path(root, cwd) if isinstance(cwd, str) and cwd.strip() else None,
                optional=item.get("optional") is True,
                env=_env(
                    item.get("env"),
                    task_name=task_name,
                    field_name=f"{field_name}[{index}].env",
                ),
            )
        )
    return tuple(commands)


def _env(raw: Any, *, task_name: str, field_name: str) -> dict[str, str]:
    if raw in (None, ""):
        return {}
    if not isinstance(raw, dict):
        raise ConfigError(f"Task '{task_name}' field {field_name} must be an object.")
    return {str(key): str(value) for key, value in raw.items()}


def _optional_schema_uri(raw: Any) -> str | None:
    if raw in (None, ""):
        return None
    if not isinstance(raw, str) or not raw.strip():
        raise ConfigError("CodepotG config $schema must be a non-empty string.")
    return raw.strip()


def _resolve_path(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (root / path).resolve()


def _reject_legacy_name(path: Path) -> None:
    if path.name in LEGACY_CONFIG_NAMES:
        raise ConfigError(
            f"{path.name} is reserved for the TypeScript Codepot workflow. "
            f"CodepotG uses {CODEPOTG_CONFIG_YAML} or {CODEPOTG_CONFIG_YML}."
        )


# Internal compatibility aliases keep the existing module graph stable.
resolve_codepot_file = resolve_codepotg_config
load_codepot_file = load_codepotg_config
load_codepot_file_yaml = load_codepotg_yaml
