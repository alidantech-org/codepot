from __future__ import annotations

from codepotg.api import CancellationToken
from codepotg.ports import SourceAdapterRequest
from codepotg_openapi import OpenApiSourceAdapter


def _normalize(content: str, *options: tuple[str, object]):
    return OpenApiSourceAdapter().normalize(
        SourceAdapterRequest(source_id="yaml", content=content, options=tuple(options)),
        CancellationToken(),
    )


def test_recursive_yaml_alias_is_rejected_without_recursion_error() -> None:
    result = _normalize(
        """openapi: 3.1.0
info: {title: Recursive, version: '1'}
paths: {}
x-recursive: &recursive
  - *recursive
""".strip()
    )
    assert result.contract is None
    assert {item.code for item in result.diagnostics} == {"OA_PARSE_YAML_ALIAS_CYCLE"}


def test_yaml_alias_expansion_is_bounded() -> None:
    result = _normalize(
        """openapi: 3.1.0
info: {title: Aliases, version: '1'}
paths: {}
x-base: &base [one, two, three]
x-expanded: [*base, *base, *base, *base]
""".strip(),
        ("maxYamlAliases", 2),
    )
    assert result.contract is None
    assert {item.code for item in result.diagnostics} == {"OA_LIMIT_YAML_ALIASES"}


def test_yaml_depth_and_expanded_node_count_are_bounded() -> None:
    deep = "value"
    for _ in range(12):
        deep = f"[{deep}]"
    depth_result = _normalize(
        f"openapi: 3.1.0\ninfo: {{title: Deep, version: '1'}}\npaths: {{}}\nx-deep: {deep}\n",
        ("maxYamlDepth", 6),
    )
    assert depth_result.contract is None
    assert {item.code for item in depth_result.diagnostics} == {"OA_LIMIT_YAML_DEPTH"}
    node_result = _normalize(
        "openapi: 3.1.0\ninfo: {title: Nodes, version: '1'}\npaths: {}\nx-values: [1, 2, 3, 4, 5]\n",
        ("maxYamlNodes", 5),
    )
    assert node_result.contract is None
    assert {item.code for item in node_result.diagnostics} == {"OA_LIMIT_YAML_NODES"}
