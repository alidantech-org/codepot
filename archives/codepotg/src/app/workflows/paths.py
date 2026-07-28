"""Application workflow for paths.yaml/paths.yml inspection."""

from __future__ import annotations

from archives.codepotg.src.app.models import (
    PathBarrelSummary,
    PathEmissionSummary,
    PathFolderSummary,
    PathProviderSummary,
    PathSelectionSummary,
    PathsInput,
    PathsOutput,
    RuntimeEvent,
)
from archives.codepotg.src.emission.paths.config_loader import load_path_config, resolve_path_config_file


def run_paths(request: PathsInput) -> PathsOutput:
    """Resolve and summarize one template pack path configuration."""

    template_root = request.template_root.expanduser().resolve()
    _notify(request, "paths_loading", f"Loading paths config: {template_root}")

    config_path = resolve_path_config_file(template_root)
    config = load_path_config(template_root, strict=True)
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
    selections = [
        PathSelectionSummary(
            name=selection.name,
            select=selection.select,
            alias=selection.alias,
            scope=selection.scope.value,
            description=selection.description,
        )
        for selection in config.selections
    ]
    emissions = [
        PathEmissionSummary(
            name=emission.name,
            selection=emission.selection,
            template=emission.template,
            output=tuple(str(part) for part in emission.output),
            providers=tuple(
                PathProviderSummary(purpose=provider.purpose, source=provider.source)
                for provider in emission.providers
            ),
            provides=emission.provides,
            lifecycle=emission.lifecycle.value if emission.lifecycle is not None else None,
            description=emission.description,
        )
        for emission in config.emissions
    ]
    barrels = [
        PathBarrelSummary(
            name=barrel.name,
            template=barrel.template,
            output=tuple(str(part) for part in barrel.output),
            exports=barrel.exports,
            scope=barrel.scope.value,
            alias=barrel.alias,
            lifecycle=barrel.lifecycle.value if barrel.lifecycle is not None else None,
            description=barrel.description,
        )
        for barrel in config.barrels
    ]
    _notify(
        request,
        "paths_resolved",
        "Resolved "
        f"{len(folders)} legacy folder recipe(s), "
        f"{len(selections)} selection(s), "
        f"{len(emissions)} emission(s), and "
        f"{len(barrels)} barrel(s)",
    )

    policy = config.write_policy
    return PathsOutput(
        template_root=template_root,
        config_path=config_path,
        template_extension=config.template_extension,
        strip_template_extension=config.strip_template_extension,
        allow_raw_files=config.allow_raw_files,
        import_strategy=config.imports.strategy,
        folders=folders,
        selections=selections,
        emissions=emissions,
        barrels=barrels,
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
