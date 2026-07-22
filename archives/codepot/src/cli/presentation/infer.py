"""Infer command renderer."""

from __future__ import annotations

import json

from rich.table import Table

from archives.codepot.src.app import InferResult
from archives.codepot.src.cli.presentation.console import console
from archives.codepot.src.cli.presentation.tables import make_key_value_table


def render_infer_result(result: InferResult) -> None:
    if result.show_paths:
        for file in result.files:
            console.print(file.path.as_posix())
        return

    console.print(f"[bold]Infer  {result.spec_path}[/bold]")
    console.print()
    console.print(
        make_key_value_table(
            "Settings",
            (
                ("Language", result.language),
                ("Template package", result.template_package_path),
                ("Output", result.output_path),
                ("Selection filter", result.select or "-"),
                ("Template IDs", ",".join(result.template_ids) or "-"),
            ),
        ),
    )
    console.print()

    table = Table(title="Planned files")
    table.add_column("Status")
    table.add_column("Path", style="cyan")
    table.add_column("Template ID")
    table.add_column("Select")
    for file in result.files:
        table.add_row(file.status, file.path.as_posix(), file.group, file.select)
    console.print(table)

    if result.show_context:
        console.print()
        console.print("[bold]Context[/bold]")
        for file in result.files:
            context = json.dumps(file.context, sort_keys=True)
            console.print(f"{file.path.as_posix()}  {context}")

    if result.show_imports:
        console.print()
        console.print("[bold]Imports[/bold]")
        for item in result.imports:
            console.print(
                f"{item['path']} imports {item['symbol']} from {item['source']}",
            )

    if result.show_dependencies:
        console.print()
        console.print("[bold]Dependencies[/bold]")
        for item in result.dependencies:
            console.print(f"{item['template']} {item['kind']} {item['target']}")

    console.print()
    console.print("No files written. Run emit to generate.")
