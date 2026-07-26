"""Go language adapter."""

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
    name="go",
    aliases=("golang",),
    format="go",
    purpose="Go API client and service contracts",
    framework="go-standard-library",
    package_suffix="client",
    package_dependencies=(
        "github.com/google/uuid",
        "github.com/shopspring/decimal",
    ),
    diagnostics=(
        "Run `go mod tidy` and `go test ./...` in the generated module.",
        "Run `gofmt -w .` before committing generated sources.",
    ),
)


@language_adapter(name=PROFILE.name, aliases=PROFILE.aliases, template_name="go")
class GoLanguageAdapter:
    """Build complete Go generation contracts."""

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
