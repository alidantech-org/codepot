"""Java language adapter."""

from __future__ import annotations

from pathlib import Path

from archives.codepotg.src.contracts.api import ApiContract
from archives.codepotg.src.contracts.emission import EmissionResult
from archives.codepotg.src.contracts.events import ProgressSink
from archives.codepotg.src.contracts.language import LanguagePostResult
from archives.codepotg.src.contracts.template import TemplateContract
from archives.codepotg.src.languages.decorators import language_adapter
from archives.codepotg.src.languages.portable import (
    PortableLanguageProfile,
    build_portable_template_contract,
    portable_after_emit,
)

PROFILE = PortableLanguageProfile(
    name="java",
    aliases=("jvm-java",),
    format="java",
    purpose="Java API client and service contracts",
    framework="jvm",
    package_suffix="client",
    package_dependencies=(
        "com.fasterxml.jackson.core:jackson-databind",
        "com.fasterxml.jackson.datatype:jackson-datatype-jsr310",
    ),
    package_dev_dependencies=("org.junit.jupiter:junit-jupiter",),
    diagnostics=(
        "Run `./mvnw test` or `./gradlew test` in the generated package.",
        "Run the configured Java formatter before committing generated sources.",
    ),
)


@language_adapter(name=PROFILE.name, aliases=PROFILE.aliases, template_name="java")
class JavaLanguageAdapter:
    """Build complete Java generation contracts."""

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
