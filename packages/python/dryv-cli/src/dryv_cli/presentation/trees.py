from __future__ import annotations

from collections import defaultdict

from dryv.generation import ArtifactPlan
from dryv.ports import ManagedWriteChange, ManagedWriteReport
from dryv.runtime import RuntimePluginInfo, RuntimeSnapshot
from rich.text import Text
from rich.tree import Tree


def plan_tree(artifacts: tuple[ArtifactPlan, ...], project_name: str) -> Tree:
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


def runtime_tree(snapshot: RuntimeSnapshot) -> Tree:
    root = Tree(_label("runtime", snapshot.core_version, "accent", "value"), guide_style="muted")
    grouped: dict[str, list[RuntimePluginInfo]] = defaultdict(list)
    for plugin in snapshot.plugins:
        grouped[plugin.category.value].append(plugin)

    for category in sorted(grouped):
        category_node = root.add(Text(category.replace("_", " "), style="identifier"))
        for plugin in grouped[category]:
            plugin_node = category_node.add(
                _label(plugin.id, f"{plugin.distribution} {plugin.version}", "command", "muted")
            )
            if plugin.aliases:
                plugin_node.add(_label("aliases", ", ".join(plugin.aliases), "muted", "value"))
            if plugin.provides:
                provides = plugin_node.add(Text("provides", style="muted"))
                for item in plugin.provides:
                    provides.add(Text(item, style="value"))
            if plugin.capabilities:
                capabilities = plugin_node.add(Text("capabilities", style="muted"))
                for item in plugin.capabilities:
                    capabilities.add(Text(item, style="value"))

    if not snapshot.plugins:
        root.add(Text("no optional plugins loaded", style="muted"))
    return root


def write_tree(report: ManagedWriteReport) -> Tree:
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
        kind_node = root.add(Text(kind, style=style))
        for change in sorted(grouped[kind], key=lambda item: item.path):
            item = kind_node.add(Text(change.path, style="path"))
            if change.reason:
                item.add(Text(change.reason, style="muted"))

    if not report.changes:
        root.add(Text("no file changes", style="muted"))
    return root


def _label(left: str, right: str, left_style: str, right_style: str) -> Text:
    text = Text()
    text.append(left, style=left_style)
    text.append(": ", style="muted")
    text.append(right, style=right_style)
    return text
