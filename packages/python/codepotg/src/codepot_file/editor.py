"""Create and edit ``Codepotg.yaml`` configuration files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from codepot_file.loader import (
    CODEPOTG_CONFIG_NAME,
    LEGACY_CONFIG_NAMES,
    load_codepotg_config,
    load_codepotg_yaml,
    resolve_codepotg_config,
)
from core.errors import ConfigError

DEFAULT_TASK_NAME = "sdk"
DEFAULT_INPUT = "./openapi.yaml"
DEFAULT_LANGUAGE = "typescript"
DEFAULT_TEMPLATE_DIR: str | None = None
DEFAULT_OUTPUT = "./generated"


class _IndentDumper(yaml.SafeDumper):
    """PyYAML dumper that indents block lists under their parent key."""

    def increase_indent(self, flow: bool = False, indentless: bool = False):
        return super().increase_indent(flow, False)


@dataclass(frozen=True)
class TaskDraft:
    """User-provided task fields before YAML serialization."""

    name: str
    input: str | None = None
    language: str | None = None
    template_dir: str | None = None
    templates: str | None = None
    output: str | None = None
    clean: tuple[str, ...] = ()
    before: tuple[str, ...] = ()
    after: tuple[str, ...] = ()


def init_codepotg_config(
    *,
    root: Path,
    draft: TaskDraft,
    force: bool = False,
) -> Path:
    """Create a new ``Codepotg.yaml`` in ``root``."""
    root = root.resolve()
    target = root / CODEPOTG_CONFIG_NAME
    existing = _existing_configs(root)

    if existing and not force:
        names = ", ".join(path.name for path in existing)
        raise ConfigError(f"CodepotG config already exists ({names}). Use --force to overwrite.")

    if force:
        for path in existing:
            if path != target:
                path.unlink()

    raw = {
        "allow": True,
        "tasks": {
            draft.name: _task_to_yaml(
                _starter_task(draft),
                allow_incomplete=False,
            )
        },
    }
    write_codepotg_config(target, raw)
    return target


def add_task_to_codepotg_config(
    *,
    config_path: Path | None,
    draft: TaskDraft,
    force: bool = False,
    yes: bool = False,
) -> Path:
    """Add or replace one task in an existing ``Codepotg.yaml``."""
    path = resolve_codepotg_config(config_path)
    loaded = load_codepotg_config(path)
    if not loaded.allow:
        raise ConfigError(f"Task editing refused. Set allow: true in {CODEPOTG_CONFIG_NAME}.")

    raw = load_codepotg_yaml(path)
    tasks = raw.setdefault("tasks", {})
    if not isinstance(tasks, dict):
        raise ConfigError("Codepotg.yaml tasks must be an object.")

    if draft.name in tasks and not force:
        raise ConfigError(f"Task '{draft.name}' already exists. Use --force to replace it.")

    defaults = raw.get("defaults") if isinstance(raw.get("defaults"), dict) else {}
    task_raw = _task_to_yaml(
        _starter_task(draft) if yes and not defaults else draft,
        allow_incomplete=bool(defaults),
    )
    _validate_resolved_task(path, draft.name, defaults, task_raw)

    tasks[draft.name] = task_raw
    write_codepotg_config(path, raw)
    return path


def starter_draft(name: str = DEFAULT_TASK_NAME) -> TaskDraft:
    """Return the default starter task using bundled templates."""
    return TaskDraft(
        name=name,
        input=DEFAULT_INPUT,
        language=DEFAULT_LANGUAGE,
        template_dir=None,
        output=DEFAULT_OUTPUT,
    )


def write_codepotg_config(path: Path, raw: dict[str, Any]) -> None:
    """Write CodepotG YAML with stable top-level ordering."""
    ordered: dict[str, Any] = {}
    if "allow" in raw:
        ordered["allow"] = raw["allow"]
    if "defaults" in raw and raw["defaults"] not in (None, {}):
        ordered["defaults"] = raw["defaults"]
    ordered["tasks"] = raw.get("tasks") or {}

    path.write_text(
        yaml.dump(
            ordered,
            Dumper=_IndentDumper,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _existing_configs(root: Path) -> list[Path]:
    names = (CODEPOTG_CONFIG_NAME, *LEGACY_CONFIG_NAMES)
    return [root / name for name in names if (root / name).exists()]


def _starter_task(draft: TaskDraft) -> TaskDraft:
    return TaskDraft(
        name=draft.name or DEFAULT_TASK_NAME,
        input=draft.input or DEFAULT_INPUT,
        language=draft.language or DEFAULT_LANGUAGE,
        template_dir=draft.template_dir,
        templates=draft.templates,
        output=draft.output or DEFAULT_OUTPUT,
        clean=draft.clean,
        before=draft.before,
        after=draft.after,
    )


def _task_to_yaml(draft: TaskDraft, *, allow_incomplete: bool) -> dict[str, Any]:
    task: dict[str, Any] = {}

    _set_optional(task, "input", draft.input)
    _set_optional(task, "language", draft.language)
    if draft.templates:
        task["templates"] = draft.templates
    else:
        _set_optional(task, "templateDir", draft.template_dir)
    _set_optional(task, "output", draft.output)

    if draft.clean:
        task["clean"] = list(draft.clean)
    if draft.before:
        task["before"] = [{"run": command} for command in draft.before]
    if draft.after:
        task["after"] = [{"run": command} for command in draft.after]

    if not allow_incomplete:
        missing = [
            field
            for field in ("input", "language", "output")
            if not isinstance(task.get(field), str) or not task[field].strip()
        ]
        if missing:
            fields = ", ".join(missing)
            raise ConfigError(f"Task '{draft.name}' is missing required fields: {fields}")

    return task


def _validate_resolved_task(
    config_path: Path,
    task_name: str,
    defaults: dict[str, Any],
    task_raw: dict[str, Any],
) -> None:
    raw = load_codepotg_yaml(config_path)
    raw["defaults"] = defaults
    raw["tasks"] = {task_name: task_raw}
    temp_path = config_path.with_name(f".{config_path.name}.tmp")
    try:
        write_codepotg_config(temp_path, raw)
        load_codepotg_config(temp_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _set_optional(target: dict[str, Any], key: str, value: str | None) -> None:
    if value is not None and value.strip():
        target[key] = value


# Internal aliases keep older module imports working while all user-facing
# behavior uses Codepotg.yaml.
init_codepot_file = init_codepotg_config
add_task_to_codepot_file = add_task_to_codepotg_config
write_codepot_file = write_codepotg_config
