from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from dryv.api import OperationResult, OperationStatus
from dryv.diagnostics import Diagnostic, DiagnosticSeverity, Diagnostics
from dryv.generation import ArtifactPlan, GenerationData
from dryv.ports import ManagedWriteChange, ManagedWriteReport
from dryv.runtime import RuntimePluginInfo, RuntimeSnapshot
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

_STATUS_STYLES = {
    OperationStatus.READY: ("✓", "success"),
    OperationStatus.GENERATED: ("✓", "success"),
    OperationStatus.GENERATED_WITH_WARNINGS: ("!", "warning"),
    OperationStatus.GENERATED_WITH_ACTIONS: ("!", "warning"),
    OperationStatus.PARTIALLY_GENERATED: ("!", "warning"),
    OperationStatus.FAILED: ("×", "error"),
    OperationStatus.CANCELLED: ("–", "warning"),
}
_SEVERITY_STYLES = {
    DiagnosticSeverity.INFO: ("i", "info"),
    DiagnosticSeverity.WARNING: ("!", "warning"),
    DiagnosticSeverity.ERROR: ("×", "error"),
    DiagnosticSeverity.FATAL: ("×", "fatal"),
}


def render_operation(
    console: Console,
    result: OperationResult[GenerationData],
    *,
    report: ManagedWriteReport | None = None,
) -> None:
    symbol, style = _STATUS_STYLES[result.status]
    heading = Text()
    heading.append(f"{symbol} ", style=style)
    heading.append(result.status.value.replace("_", " "), style=style)
    heading.append(f"  operation {result.operation_id[:10]}", style="muted")
    console.print(heading)

    if result.diagnostics:
        console.print()
        console.print(_diagnostics_tree(result.diagnostics))

    if result.data is not None:
        console.print()
        console.print(_plan_tree(result.data.plan.artifacts, result.data.plan.project_name))
        if result.data.output is not None:
            console.print()
            _render_output_summary(console, result.data)

    if report is not None:
        console.print()
        console.print(_write_tree(report))


def render_runtime(console: Console, snapshot: RuntimeSnapshot) -> None:
    root = Tree(_label("runtime", snapshot.core_version, "accent", "value"), guide_style="muted")
    grouped: dict[str, list[RuntimePluginInfo]] = defaultdict(list)
    for plugin in snapshot.plugins:
        grouped[plugin.category.value].append(plugin)

    for category in sorted(grouped):
        category_node = root.add(_plain_label(category.replace("_", " "), "identifier"))
        for plugin in grouped[category]:
            plugin_node = category_node.add(
                _label(plugin.id, f"{plugin.distribution} {plugin.version}", "command", "muted")
            )
            if plugin.aliases:
                plugin_node.add(_label("aliases", ", ".join(plugin.aliases), "muted", "value"))
            if plugin.provides:
                provides = plugin_node.add(_plain_label("provides", "muted"))
                for item in plugin.provides:
                    provides.add(Text(item, style="value"))
            if plugin.capabilities:
                capabilities = plugin_node.add(_plain_label("capabilities", "muted"))
                for item in plugin.capabilities:
                    capabilities.add(Text(item, style="value"))

    if not snapshot.plugins:
        root.add(Text("no optional plugins loaded", style="muted"))
    console.print(root)


def render_failure(console: Console, message: str, *, code: str = "CLI_FAILED") -> None:
    line = Text()
    line.append("× ", style="error")
    line.append(code, style="error")
    line.append("  ")
    line.append(message, style="value")
    console.print(line)


def render_cancelled(console: Console, message: str = "Generation cancelled.") -> None:
    line = Text()
    line.append("– ", style="warning")
    line.append(message, style="value")
    console.print(line)


def render_json(console: Console, document: dict[str, Any]) -> None:
    payload = json.dumps(document, indent=2, sort_keys=True)
    console.print(payload, markup=False, highlight=False, soft_wrap=True)


def _diagnostics_tree(diagnostics: Diagnostics) -> Tree:
    root = Tree(_plain_label("diagnostics", "accent"), guide_style="muted")
    for diagnostic in diagnostics:
        root.add(_diagnostic_tree(diagnostic))
    return root


def _diagnostic_tree(diagnostic: Diagnostic) -> Tree:
    symbol, style = _SEVERITY_STYLES[diagnostic.severity]
    heading = Text()
    heading.append(f"{symbol} ", style=style)
    heading.append(diagnostic.code, style=style)
    heading.append("  ")
    heading.append(diagnostic.message, style="value")
    node = Tree(heading, guide_style="muted")

    if diagnostic.span is not None:
        location = (
            f"{diagnostic.span.source.value}:"
            f"{diagnostic.span.start.line}:{diagnostic.span.start.column}"
        )
        node.add(_label("location", location, "muted", "path"))
    for key, value in diagnostic.details:
        node.add(_label(key, str(value), "muted", "value"))
    if diagnostic.suggestion:
        node.add(_label("suggestion", diagnostic.suggestion, "muted", "success"))
    if diagnostic.documentation:
        node.add(_label("documentation", diagnostic.documentation, "muted", "path"))
    return node


def _plan_tree(artifacts: tuple[ArtifactPlan, ...], project_name: str) -> Tree:
    root = Tree(_label("project", project_name, "accent", "value"), guide_style="muted")
    grouped: dict[tuple[str, str], list[ArtifactPlan]] = defaultdict(list)
    for artifact in artifacts:
        grouped[(artifact.pack_instance, artifact.pack_id)].append(artifact)

    for pack_instance, pack_id in sorted(grouped):
        pack_node = root.add(_label(pack_instance, pack_id, "command", "muted"))
        for artifact in sorted(grouped[(pack_instance, pack_id)], key=lambda item: item.output_path):
            artifact_node = pack_node.add(
                _label(artifact.output_path, artifact.kind.value, "path", "muted")
            )
            if artifact.selection_key:
                artifact_node.add(
                    _label("selection", artifact.selection_key, "muted", "identifier")
                )
            if artifact.semantic_id:
                artifact_node.add(
                    _label("semantic", artifact.semantic_id, "muted", "identifier")
                )
            if artifact.target_id:
                artifact_node.add(_label("target", artifact.target_id, "muted", "value"))
            artifact_node.add(_label("template", artifact.template_id, "muted", "path"))

    if not artifacts:
        root.add(Text("no artifacts planned", style="muted"))
    return root


def _render_output_summary(console: Console, data: GenerationData) -> None:
    output = data.output
    if output is None:
        return
    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="muted")
    summary.add_column(style="value", justify="right")
    summary.add_row("generated files", str(len(output.artifacts)))
    summary.add_row("generated bytes", str(sum(len(item.content) for item in output.artifacts)))
    console.print(summary)


def _write_tree(report: ManagedWriteReport) -> Tree:
    root = Tree(_label("managed output", report.state_path, "accent", "path"), guide_style="muted")
    grouped: dict[str, list[ManagedWriteChange]] = defaultdict(list)
    for change in report.changes:
        grouped[change.kind.value].append(change)

    for kind in sorted(grouped):
        style = {
            "create": "success",
            "change": "warning",
            "delete": "error",
            "leave": "muted",
            "protect": "warning",
        }.get(kind, "value")
        kind_node = root.add(_plain_label(kind, style))
        for change in sorted(grouped[kind], key=lambda item: item.path):
            item = kind_node.add(Text(change.path, style="path"))
            if change.reason:
                item.add(Text(change.reason, style="muted"))

    if not report.changes:
        root.add(Text("no file changes", style="muted"))
    return root


def _plain_label(value: str, style: str) -> Text:
    return Text(value, style=style)


def _label(left: str, right: str, left_style: str, right_style: str) -> Text:
    text = Text()
    text.append(left, style=left_style)
    text.append(": ", style="muted")
    text.append(right, style=right_style)
    return text
