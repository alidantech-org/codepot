"""Python language adapter."""

from __future__ import annotations

from pathlib import Path

from contracts.api import ApiContract
from contracts.emission import EmissionResult
from contracts.events import ProgressSink
from contracts.language import LanguagePostResult
from contracts.template import TemplateContract
from languages.decorators import language_adapter
from languages.portable import (
    PortableLanguageProfile,
    build_portable_template_contract,
    portable_after_emit,
)

PROFILE = PortableLanguageProfile(
    name="python",
    aliases=("py",),
    format="python",
    purpose="Python API client and service contracts",
    framework="python-standard-library",
    package_suffix="client",
    diagnostics=(
        "Run `python -m pip install -e .` when package metadata is emitted.",
        "Run `python -m ruff format .` after generation when Ruff is available.",
    ),
)


@language_adapter(name=PROFILE.name, aliases=PROFILE.aliases, template_name="python")
class PythonLanguageAdapter:
    """Expose the complete typed contract to Python templates."""

    name: str
    aliases: tuple[str, ...]
    template_name: str

    def build_template_contract(
        self,
        *,
        api: ApiContract,
        output_path: Path,
        template_root: Path | None = None,
        dry_run: bool = False,
        frontend: str | None = None,
        progress: ProgressSink | None = None,
    ) -> TemplateContract:
        return build_portable_template_contract(
            PROFILE,
            api=api,
            output_path=output_path,
            template_root=template_root,
            dry_run=dry_run,
            frontend=frontend,
            progress=progress,
        )

    def after_emit(
        self,
        *,
        result: EmissionResult,
        progress: ProgressSink | None = None,
    ) -> LanguagePostResult:
        return portable_after_emit(PROFILE, result=result, progress=progress)
