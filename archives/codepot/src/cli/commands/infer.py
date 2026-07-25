"""Plan command."""

from __future__ import annotations

import typer
from archives.codepot.src.app import codepotx
from archives.codepot.src.cli.options import (
    DEFAULT_OUTPUT_OPTION,
    DEFAULT_TEMPLATE_PACKAGE_OPTION,
    DebugOption,
    LanguageOption,
    OutputPathOption,
    SelectOption,
    SpecPathArg,
    TemplateIdsOption,
    TemplatePackageOption,
    VerboseOption,
)
from archives.codepot.src.cli.presentation.console import print_error
from archives.codepot.src.cli.presentation.pipeline import (
    print_pipeline_event,
    print_pipeline_report,
)
from archives.codepot.src.pipeline.contracts.options import PipelineOptions
from archives.codepot.src.pipeline.contracts.results import PassStatus


def plan_command(
    spec_path: SpecPathArg,
    template_package_path: TemplatePackageOption = DEFAULT_TEMPLATE_PACKAGE_OPTION,
    output_path: OutputPathOption = DEFAULT_OUTPUT_OPTION,
    language: LanguageOption = None,
    select: SelectOption = (),
    template_ids: TemplateIdsOption = (),
    debug: DebugOption = False,
    verbose: VerboseOption = False,
) -> None:
    """Plan generated files without rendering or writing."""

    options = PipelineOptions(
        spec_path=spec_path,
        template_package_path=template_package_path,
        output_path=output_path,
        language=language,
        select=tuple(select),
        template_ids=tuple(template_ids),
        dry_run=True,
        debug=debug,
        verbose=verbose,
        render=False,
        write=False,
        write_graph=False,
    )

    try:
        result = codepotx.plan(
            options,
            reporter=print_pipeline_event if verbose or debug else None,
        )
    except Exception as error:
        print_error(str(error))
        raise typer.Exit(code=1) from error

    print_pipeline_report(result.report)

    if result.report.status == PassStatus.FAILED:
        raise typer.Exit(code=1)
