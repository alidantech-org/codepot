"""Application workflow for paths.yaml/paths.yml inspection."""

from __future__ import annotations

from app.models import PathFolderSummary, PathsInput, PathsOutput, RuntimeEvent
from emission.paths.config_loader import load_path_config, resolve_path_config_file


def run_paths(request: PathsInput) -> PathsOutput:
    """Resolve and summarize one template pack path configuration."""
    template_root = request.template_root.expanduser().resolve()
    _notify(request, "paths_loading", f"Loading paths config: {template_root}")

    config_path = resolve_path_config_file(template_root)
    config = load_path_config(template_root)
    folders = [
        PathFolderSummary(
            name=folder.name,
            select=folder.select,
            alias=folder.alias,
            mode=folder.mode.value,
            lifecycle=folder.lifecycle.value if folder.lifecycle is not None else None,
            parts=tuple(str(part) for part in folder.parts),
            description=folder.description,
        )
        for folder in config.folders
    ]
    _notify(request, "paths_resolved", f"Resolved {len(folders)} folder recipe(s)")

    policy = config.write_policy
    return PathsOutput(
        template_root=template_root,
        config_path=config_path,
        template_extension=config.template_extension,
        strip_template_extension=config.strip_template_extension,
        allow_raw_files=config.allow_raw_files,
        import_strategy=config.imports.strategy,
        folders=folders,
        default_lifecycle=policy.default_mode.value,
        managed_roots=policy.managed_roots,
        immutable_roots=policy.immutable_roots,
        protected_roots=policy.protected_roots,
        clean_roots=policy.clean_roots,
    )


def _notify(request: PathsInput, stage: str, message: str) -> None:
    if request.progress is None:
        return
    request.progress(RuntimeEvent(stage=stage, message=message))
