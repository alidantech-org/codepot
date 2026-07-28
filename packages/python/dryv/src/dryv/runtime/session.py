from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dryv.api import (
    CancellationToken,
    OperationCancelled,
    OperationResult,
    OperationStatus,
)
from dryv.config import PackManifest, ProjectConfig, load_pack_manifest
from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity
from dryv.generation.context import RenderContextBuilder
from dryv.generation.manifest_validation import require_pack_contained
from dryv.generation.models import (
    GeneratedArtifact,
    GenerationData,
    GenerationPlan,
    MemoryOutput,
    PackFileKind,
)
from dryv.generation.planner import ProjectPlanner
from dryv.ir import Contract
from dryv.ports import RenderRequest, SourceAdapterRequest

from .plugins import PluginLoadError, RuntimePlugins


@dataclass(slots=True)
class GenerationSession:
    plugins: RuntimePlugins

    def generate(
        self,
        *,
        project: ProjectConfig,
        project_root: str | Path,
        cancellation: CancellationToken | None = None,
        dry_run: bool = False,
    ) -> OperationResult[GenerationData]:
        token = cancellation or CancellationToken()
        diagnostics = Diagnostics()
        try:
            root = Path(project_root).resolve(strict=True)
            token.raise_if_cancelled()
            self._authorize_project(project, root)
            contracts, source_diagnostics = self._normalize_sources(project, root, token)
            diagnostics = diagnostics.extend(source_diagnostics)
            if diagnostics.has_errors:
                return self._failed(project, diagnostics)

            planner = ProjectPlanner(plugins=self.plugins)
            planned = planner.plan(
                project=project,
                project_root=root,
                contracts=contracts,
            )
            diagnostics = diagnostics.extend(planned.diagnostics)
            plan = GenerationPlan(project.name, planned.artifacts, diagnostics)
            if diagnostics.has_errors:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    data=GenerationData(plan=plan),
                    diagnostics=diagnostics,
                )
            if dry_run:
                return OperationResult(
                    status=OperationStatus.READY,
                    data=GenerationData(plan=plan),
                    diagnostics=diagnostics,
                )

            output, render_diagnostics = self._render(
                project=project,
                project_root=root,
                contracts=contracts,
                plan=plan,
                cancellation=token,
            )
            diagnostics = diagnostics.extend(render_diagnostics)
            if diagnostics.has_errors:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    data=GenerationData(plan=plan),
                    diagnostics=diagnostics,
                )
            status = (
                OperationStatus.GENERATED_WITH_WARNINGS
                if diagnostics
                else OperationStatus.GENERATED
            )
            return OperationResult(
                status=status,
                data=GenerationData(plan=plan, output=output),
                diagnostics=diagnostics,
            )
        except OperationCancelled:
            diagnostics = diagnostics.add(
                _diagnostic("GENERATION_CANCELLED", "generation was cancelled")
            )
            return OperationResult(
                status=OperationStatus.CANCELLED,
                diagnostics=diagnostics,
            )
        except (ValueError, PluginLoadError, OSError, UnicodeError) as exc:
            diagnostics = diagnostics.add(_exception_diagnostic(exc))
            return self._failed(project, diagnostics)

    @staticmethod
    def _authorize_project(project: ProjectConfig, root: Path) -> None:
        for pack in project.packs:
            if pack.source.local is not None:
                require_pack_contained(root / pack.source.local, root)
        for source in project.sources:
            _require_project_contained(root / source.file, root, "SOURCE_PATH_ESCAPE")

    def _normalize_sources(
        self,
        project: ProjectConfig,
        root: Path,
        cancellation: CancellationToken,
    ) -> tuple[dict[str, Contract], Diagnostics]:
        contracts: dict[str, Contract] = {}
        diagnostics = Diagnostics()
        for source in project.sources:
            cancellation.raise_if_cancelled()
            adapter = self.plugins.source(source.adapter)
            location = _require_project_contained(
                root / source.file,
                root,
                "SOURCE_PATH_ESCAPE",
            )
            result = adapter.normalize(
                SourceAdapterRequest(
                    source_id=source.name,
                    location=str(location),
                    options=source.options,
                ),
                cancellation,
            )
            diagnostics = diagnostics.extend(result.diagnostics)
            if result.contract is not None:
                contracts[source.name] = result.contract
        return contracts, diagnostics

    def _render(
        self,
        *,
        project: ProjectConfig,
        project_root: Path,
        contracts: dict[str, Contract],
        plan: GenerationPlan,
        cancellation: CancellationToken,
    ) -> tuple[MemoryOutput, Diagnostics]:
        generated: list[GeneratedArtifact] = []
        diagnostics = Diagnostics()
        instances = {item.name: item for item in project.packs}
        manifest_cache: dict[str, PackManifest] = {}

        for artifact in plan.artifacts:
            cancellation.raise_if_cancelled()
            if artifact.kind is PackFileKind.STATIC:
                assert artifact.content is not None
                generated.append(
                    GeneratedArtifact(
                        id=artifact.id,
                        path=artifact.output_path,
                        content=artifact.content,
                        target_id=artifact.target_id,
                        template_id=artifact.template_id,
                        semantic_id=artifact.semantic_id,
                    )
                )
                continue

            instance = instances[artifact.pack_instance]
            if instance.source.local is None:
                diagnostics = diagnostics.add(
                    _diagnostic(
                        "PACK_PROVIDER_UNSUPPORTED",
                        "rendering currently supports local packs only",
                        pack_instance=instance.name,
                    )
                )
                continue
            pack_root = require_pack_contained(
                project_root / instance.source.local,
                project_root,
            )
            cache_key = pack_root.as_posix()
            manifest = manifest_cache.get(cache_key)
            if manifest is None:
                manifest = load_pack_manifest(pack_root / "DryvPack.yaml")
                manifest_cache[cache_key] = manifest
            options = manifest.resolve_options(instance.options)
            contract = contracts.get(instance.input) if instance.input is not None else None
            if contract is None:
                diagnostics = diagnostics.add(
                    _diagnostic(
                        "PLAN_TEMPLATE_INPUT_REQUIRED",
                        "rendered templates require a semantic input",
                        artifact=artifact.id,
                    )
                )
                continue
            context = RenderContextBuilder(contract).build(
                selection=artifact.context,
                project=project,
                manifest=manifest,
                artifact=artifact,
                options=options,
                bindings=instance.bindings,
            )
            try:
                source_text = (artifact.content or b"").decode("utf-8")
            except UnicodeDecodeError:
                diagnostics = diagnostics.add(
                    _diagnostic(
                        "TEMPLATE_ENCODING_INVALID",
                        "template source must be UTF-8",
                        template=artifact.template_id,
                    )
                )
                continue
            engine = self.plugins.engine(artifact.engine_id or "")
            result = engine.render(
                RenderRequest(
                    template_id=artifact.template_id,
                    source=source_text,
                    context=context,
                    partials=artifact.partials,
                ),
                cancellation,
            )
            diagnostics = diagnostics.extend(result.diagnostics)
            if result.content is None:
                continue
            generated.append(
                GeneratedArtifact(
                    id=artifact.id,
                    path=artifact.output_path,
                    content=result.content.encode("utf-8"),
                    target_id=artifact.target_id,
                    template_id=artifact.template_id,
                    semantic_id=artifact.semantic_id,
                )
            )

        return MemoryOutput(tuple(sorted(generated, key=lambda item: item.path))), diagnostics

    @staticmethod
    def _failed(
        project: ProjectConfig,
        diagnostics: Diagnostics,
    ) -> OperationResult[GenerationData]:
        plan = GenerationPlan(project.name, (), diagnostics)
        return OperationResult(
            status=OperationStatus.FAILED,
            data=GenerationData(plan=plan),
            diagnostics=diagnostics,
        )


def _require_project_contained(path: Path, root: Path, code: str) -> Path:
    canonical = path.resolve(strict=True)
    try:
        canonical.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{code}: path escapes the project root") from exc
    return canonical


def _exception_diagnostic(exc: Exception) -> Diagnostic:
    code = getattr(exc, "code", None)
    if not isinstance(code, str):
        text = str(exc)
        code = text.split(":", 1)[0] if ":" in text else "GENERATION_FAILED"
    message = getattr(exc, "message", None)
    if not isinstance(message, str):
        message = str(exc) or "generation failed"
    return _diagnostic(code, message, exception_type=type(exc).__name__)


def _diagnostic(code: str, message: str, **details: object) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity=DiagnosticSeverity.ERROR,
        message=message,
        details=tuple(sorted(details.items())),
    )
