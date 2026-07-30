from __future__ import annotations

from dataclasses import dataclass

from jinja2 import Environment, TemplateAssertionError, TemplateSyntaxError, nodes

from dryv.api import CancellationToken
from dryv_template_jinja.rules import JinjaEngineRules

from .dependencies import DependencyEdge, DependencyKind
from .registry import TemplateRegistry, TemplateRegistryError, validate_template_id


class TemplateAnalysisError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        template_id: str,
        line: int | None = None,
        details: tuple[tuple[str, object], ...] = (),
    ) -> None:
        super().__init__(message)
        self.code = code
        self.template_id = template_id
        self.line = line
        self.details = details


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    reachable_partial_ids: tuple[str, ...]
    edges: tuple[DependencyEdge, ...]
    ast_nodes: int


def analyze_dependencies(
    environment: Environment,
    registry: TemplateRegistry,
    rules: JinjaEngineRules,
    cancellation: CancellationToken,
) -> AnalysisResult:
    edges: list[DependencyEdge] = []
    reachable: set[str] = set()
    parsed: set[str] = set()
    total_ast_nodes = 0

    def visit(template_id: str, stack: tuple[str, ...], depth: int) -> None:
        nonlocal total_ast_nodes
        cancellation.raise_if_cancelled()
        if template_id in parsed:
            return
        try:
            tree = environment.parse(
                registry.source(template_id),
                name=template_id,
                filename=template_id,
            )
        except (TemplateSyntaxError, TemplateAssertionError) as exc:
            failed_id = getattr(exc, "name", None) or template_id
            raise TemplateAnalysisError(
                "JINJA_SYNTAX",
                "template syntax is invalid",
                template_id=failed_id,
                line=getattr(exc, "lineno", None),
                details=(
                    ("exception_type", type(exc).__name__),
                    ("template_id", failed_id),
                ),
            ) from exc

        node_count = _count_nodes(tree)
        total_ast_nodes += node_count
        if total_ast_nodes > rules.max_ast_nodes:
            raise TemplateAnalysisError(
                "JINJA_TEMPLATE_TOO_LARGE",
                "reachable template AST exceeds the configured node limit",
                template_id=template_id,
                details=(
                    ("actual_nodes", total_ast_nodes),
                    ("max_nodes", rules.max_ast_nodes),
                    ("template_id", template_id),
                ),
            )

        parsed.add(template_id)
        dependencies = tuple(sorted(_extract_dependencies(tree, template_id)))
        for edge in dependencies:
            cancellation.raise_if_cancelled()
            try:
                validate_template_id(edge.target_id, rules, root=False)
            except TemplateRegistryError as exc:
                raise TemplateAnalysisError(
                    "JINJA_PARTIAL_INVALID",
                    "declared template dependency has an invalid registry ID",
                    template_id=template_id,
                    line=edge.line,
                    details=(
                        ("dependency_id", edge.target_id),
                        ("dependency_kind", edge.kind.value),
                        ("template_id", template_id),
                    ),
                ) from exc

            if edge.target_id in (*stack, template_id):
                cycle = (*stack, template_id, edge.target_id)
                raise TemplateAnalysisError(
                    "JINJA_INCLUDE_CYCLE",
                    "declared template dependencies contain a cycle",
                    template_id=template_id,
                    line=edge.line,
                    details=(
                        ("dependency_id", edge.target_id),
                        ("include_stack", " -> ".join(cycle)),
                        ("template_id", template_id),
                    ),
                )
            if not registry.has_partial(edge.target_id):
                raise TemplateAnalysisError(
                    "JINJA_INCLUDE_MISSING",
                    "declared template dependency is missing from request.partials",
                    template_id=template_id,
                    line=edge.line,
                    details=(
                        ("dependency_id", edge.target_id),
                        ("dependency_kind", edge.kind.value),
                        ("include_stack", " -> ".join((*stack, template_id, edge.target_id))),
                        ("template_id", template_id),
                    ),
                )
            next_depth = depth + 1
            if next_depth > rules.max_include_depth:
                raise TemplateAnalysisError(
                    "JINJA_INCLUDE_DEPTH",
                    "declared template dependencies exceed the configured depth limit",
                    template_id=template_id,
                    line=edge.line,
                    details=(
                        ("actual_depth", next_depth),
                        ("dependency_id", edge.target_id),
                        ("include_stack", " -> ".join((*stack, template_id, edge.target_id))),
                        ("max_depth", rules.max_include_depth),
                    ),
                )
            edges.append(edge)
            reachable.add(edge.target_id)
            visit(edge.target_id, (*stack, template_id), next_depth)

    visit(registry.root_id, (), 0)
    return AnalysisResult(
        reachable_partial_ids=tuple(sorted(reachable)),
        edges=tuple(sorted(set(edges))),
        ast_nodes=total_ast_nodes,
    )


def _extract_dependencies(tree: nodes.Template, template_id: str) -> tuple[DependencyEdge, ...]:
    result: list[DependencyEdge] = []
    dependency_nodes = (nodes.Include, nodes.Extends, nodes.Import, nodes.FromImport)
    for node in tree.find_all(dependency_nodes):
        kind = _dependency_kind(node)
        if isinstance(node, nodes.Include) and node.ignore_missing:
            raise TemplateAnalysisError(
                "JINJA_INCLUDE_DYNAMIC",
                "include 'ignore missing' behavior is disabled",
                template_id=template_id,
                line=node.lineno,
                details=(
                    ("dependency_kind", kind.value),
                    ("reason", "ignore_missing"),
                    ("template_id", template_id),
                ),
            )
        target = node.template
        if not isinstance(target, nodes.Const) or not isinstance(target.value, str):
            raise TemplateAnalysisError(
                "JINJA_INCLUDE_DYNAMIC",
                "template dependencies must use one static string identifier",
                template_id=template_id,
                line=node.lineno,
                details=(
                    ("dependency_kind", kind.value),
                    ("template_id", template_id),
                ),
            )
        result.append(
            DependencyEdge(
                source_id=template_id,
                target_id=target.value,
                kind=kind,
                line=node.lineno,
            )
        )
    return tuple(result)


def _dependency_kind(node: nodes.Node) -> DependencyKind:
    if isinstance(node, nodes.Extends):
        return DependencyKind.EXTENDS
    if isinstance(node, nodes.FromImport):
        return DependencyKind.FROM_IMPORT
    if isinstance(node, nodes.Import):
        return DependencyKind.IMPORT
    return DependencyKind.INCLUDE


def _count_nodes(root: nodes.Node) -> int:
    count = 0
    pending = [root]
    while pending:
        current = pending.pop()
        count += 1
        pending.extend(current.iter_child_nodes())
    return count
