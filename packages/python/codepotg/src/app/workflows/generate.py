"""CodepotFile-driven generation workflow."""

from __future__ import annotations

from app.models import (
    GenerateInput,
    GenerateOutput,
    GenerateTaskOutput,
    RuntimeDiagnostic,
    RuntimeEvent,
)
from app.models.inputs import EmitInput
from app.workflows.emit import run_emit
from app.workflows.template_paths import resolve_template_root
from codepot_file.loader import load_codepot_file
from codepot_file.models import CodepotFile, CodepotTask
from codepot_file.runner import clean_task_paths, run_commands
from core.errors import CommandError, ConfigError
from emission.paths.config_loader import load_path_config
from languages.discovery import resolve_language_adapter


def run_generate(request: GenerateInput) -> GenerateOutput:
    """Run one or more CodepotFile tasks."""
    _notify(request, "loading_config", "Loading config")
    config = load_codepot_file(request.config_path)
    if not config.allow:
        raise ConfigError("Generation refused. Set allow: true in CodepotFile.yml to enable it.")

    _notify(request, "resolving_task", "Resolving task")
    selected_tasks = _select_tasks(config, task_name=request.task_name, all_tasks=request.all_tasks)
    outputs: list[GenerateTaskOutput] = []
    diagnostics: list[RuntimeDiagnostic] = []

    for task in selected_tasks:
        _notify(request, "resolving_task", f"Resolving task: {task.name}")
        _notify(request, "validating_task", f"Validating task: {task.name}")
        task_output = _run_task(task, config=config, request=request)
        outputs.append(task_output)
        diagnostics.extend(task_output.diagnostics)

    return GenerateOutput(
        config_path=config.path,
        dry_run=request.dry_run,
        tasks=outputs,
        diagnostics=diagnostics,
    )


def _select_tasks(
    config: CodepotFile,
    *,
    task_name: str | None,
    all_tasks: bool,
) -> tuple[CodepotTask, ...]:
    if all_tasks and task_name:
        raise ConfigError("Pass either a task name or --all, not both.")

    if all_tasks:
        return config.tasks

    if task_name:
        for task in config.tasks:
            if task.name == task_name:
                return (task,)
        available = ", ".join(task.name for task in config.tasks)
        raise ConfigError(f"Unknown task '{task_name}'. Available tasks: {available}")

    if len(config.tasks) == 1:
        return (config.tasks[0],)

    available = "\n".join(f"  - {task.name}" for task in config.tasks)
    raise ConfigError(
        f"Multiple tasks found. Pass a task name or --all.\nAvailable tasks:\n{available}"
    )


def _run_task(
    task: CodepotTask,
    *,
    config: CodepotFile,
    request: GenerateInput,
) -> GenerateTaskOutput:
    diagnostics: list[RuntimeDiagnostic] = [
        RuntimeDiagnostic(level="info", message=f"Running task: {task.name}")
    ]
    cleaned = []
    adapter = resolve_language_adapter(task.language)
    template_root = resolve_template_root(adapter=adapter, templates_path=task.template_dir)
    path_config = load_path_config(template_root)

    if request.refresh:
        _notify(request, "cleaning_paths", "Cleaning configured paths")
        clean_result = clean_task_paths(
            task,
            config_root=config.root,
            dry_run=request.dry_run,
            write_policy=path_config.write_policy,
        )
        cleaned = clean_result.cleaned
        diagnostics.extend(
            RuntimeDiagnostic(level="info", message=item) for item in clean_result.diagnostics
        )

    if not request.skip_before:
        _notify(request, "before_commands", "Running before commands")
        try:
            before_result = run_commands(
                task.before,
                task=task,
                config_root=config.root,
                dry_run=request.dry_run,
                verbose=request.verbose,
                phase="before",
                progress=request.progress,
            )
        except CommandError as exc:
            raise CommandError(f"Task failed: {task.name}\n  Stage: before command\n{exc}") from exc
        diagnostics.extend(
            RuntimeDiagnostic(
                level="warning" if "Optional command failed" in item else "info",
                message=item,
            )
            for item in before_result.diagnostics
        )

    _notify(request, "loading_openapi", f"Loading OpenAPI document: {task.input}")
    emit_result = run_emit(
        EmitInput(
            input_path=task.input,
            language=task.language,
            output_path=task.output,
            dry_run=request.dry_run,
            templates_path=task.template_dir,
            frontend=task.frontend,
            progress=request.progress,
        )
    )
    diagnostics.extend(emit_result.diagnostics)

    if not request.skip_after and not request.dry_run:
        _notify(request, "after_commands", "Running after commands")
        try:
            after_result = run_commands(
                task.after,
                task=task,
                config_root=config.root,
                dry_run=False,
                verbose=request.verbose,
                phase="after",
                progress=request.progress,
            )
        except CommandError as exc:
            raise CommandError(f"Task failed: {task.name}\n  Stage: after command\n{exc}") from exc
        diagnostics.extend(
            RuntimeDiagnostic(
                level="warning" if "Optional command failed" in item else "info",
                message=item,
            )
            for item in after_result.diagnostics
        )
    elif not request.skip_after and request.dry_run:
        _notify(request, "after_commands", "Running after commands")
        after_result = run_commands(
            task.after,
            task=task,
            config_root=config.root,
            dry_run=True,
            verbose=request.verbose,
            phase="after",
            progress=request.progress,
        )
        diagnostics.extend(
            RuntimeDiagnostic(level="info", message=item) for item in after_result.diagnostics
        )

    return GenerateTaskOutput(
        name=task.name,
        input_path=task.input,
        language=task.language,
        output_path=task.output,
        template_dir=task.template_dir,
        dry_run=request.dry_run,
        planned=emit_result.planned,
        written=emit_result.written,
        updated=emit_result.updated,
        unchanged=emit_result.unchanged,
        skipped=emit_result.skipped,
        immutable_created=emit_result.immutable_created,
        immutable_skipped=emit_result.immutable_skipped,
        refused=emit_result.refused,
        cleaned=cleaned,
        diagnostics=diagnostics,
    )


def _notify(
    request: GenerateInput,
    stage: str,
    message: str,
    *,
    level: str = "info",
) -> None:
    if request.progress is None:
        return
    request.progress(RuntimeEvent(stage=stage, message=message, level=level))
