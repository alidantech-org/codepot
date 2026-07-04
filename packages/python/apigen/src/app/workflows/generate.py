"""CodepotFile-driven generation workflow."""

from __future__ import annotations

from app.models import GenerateInput, GenerateOutput, GenerateTaskOutput, RuntimeDiagnostic
from app.models.inputs import EmitInput
from app.workflows.emit import run_emit
from codepot_file.loader import load_codepot_file
from codepot_file.models import CodepotFile, CodepotTask
from codepot_file.runner import clean_task_paths, run_commands
from core.errors import ConfigError


def run_generate(request: GenerateInput) -> GenerateOutput:
    """Run one or more CodepotFile tasks."""
    config = load_codepot_file(request.config_path)
    if not config.allow:
        raise ConfigError("Generation refused. Set allow: true in CodepotFile.yml to enable it.")

    selected_tasks = _select_tasks(config, task_name=request.task_name, all_tasks=request.all_tasks)
    outputs: list[GenerateTaskOutput] = []
    diagnostics: list[RuntimeDiagnostic] = []

    for task in selected_tasks:
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

    if request.refresh:
        clean_result = clean_task_paths(task, config_root=config.root, dry_run=request.dry_run)
        cleaned = clean_result.cleaned
        diagnostics.extend(
            RuntimeDiagnostic(level="info", message=item) for item in clean_result.diagnostics
        )

    if not request.skip_before:
        before_result = run_commands(
            task.before,
            task=task,
            config_root=config.root,
            dry_run=request.dry_run,
            verbose=request.verbose,
        )
        diagnostics.extend(
            RuntimeDiagnostic(
                level="warning" if "Optional command failed" in item else "info",
                message=item,
            )
            for item in before_result.diagnostics
        )

    emit_result = run_emit(
        EmitInput(
            input_path=task.input,
            language=task.language,
            output_path=task.output,
            dry_run=request.dry_run,
            templates_path=task.template_dir,
            progress=request.progress,
        )
    )
    diagnostics.extend(emit_result.diagnostics)

    if not request.skip_after and not request.dry_run:
        after_result = run_commands(
            task.after,
            task=task,
            config_root=config.root,
            dry_run=False,
            verbose=request.verbose,
        )
        diagnostics.extend(
            RuntimeDiagnostic(
                level="warning" if "Optional command failed" in item else "info",
                message=item,
            )
            for item in after_result.diagnostics
        )
    elif not request.skip_after and request.dry_run:
        after_result = run_commands(
            task.after,
            task=task,
            config_root=config.root,
            dry_run=True,
            verbose=request.verbose,
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
        cleaned=cleaned,
        diagnostics=diagnostics,
    )
