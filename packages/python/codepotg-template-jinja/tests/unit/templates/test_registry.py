from __future__ import annotations

from types import SimpleNamespace

import pytest

from codepotg.ports import RenderRequest
from codepotg_template_jinja import JinjaEngineRules
from codepotg_template_jinja.templates import TemplateRegistry, TemplateRegistryError


def create(
    *,
    template_id: str = "root.jinja",
    source: str = "ok",
    partials: tuple[tuple[str, str], ...] = (),
    rules: JinjaEngineRules | None = None,
) -> TemplateRegistry:
    return TemplateRegistry.create(
        RenderRequest(template_id, source, (), partials), rules or JinjaEngineRules()
    )


@pytest.mark.parametrize(
    "template_id",
    ["/absolute.jinja", "C:/drive.jinja", "../up.jinja", "a/../b.jinja", "a\\b.jinja", "a//b.jinja", "a\x00b"],
)
def test_root_template_ids_are_registry_identifiers_not_paths(template_id: str) -> None:
    with pytest.raises(TemplateRegistryError) as captured:
        create(template_id=template_id)
    assert captured.value.code == "JINJA_TEMPLATE_ID_INVALID"


def test_root_and_partial_ids_must_not_collide() -> None:
    with pytest.raises(TemplateRegistryError, match="collide"):
        create(partials=(("root.jinja", "x"),))


def test_partial_ids_must_be_sorted() -> None:
    request = SimpleNamespace(
        template_id="root.jinja",
        source="ok",
        partials=(("z.jinja", "z"), ("a.jinja", "a")),
    )
    with pytest.raises(TemplateRegistryError, match="sorted"):
        TemplateRegistry.create(request, JinjaEngineRules())  # type: ignore[arg-type]


def test_newlines_are_normalized_before_rendering_identity() -> None:
    left = create(source="a\r\nb\r")
    right = create(source="a\nb\n")
    assert left.root_source == right.root_source == "a\nb\n"


def test_root_and_partial_size_limits_are_enforced() -> None:
    rules = JinjaEngineRules(max_template_bytes=3, max_partial_bytes=10)
    with pytest.raises(TemplateRegistryError) as root_error:
        create(source="four", rules=rules)
    assert root_error.value.code == "JINJA_TEMPLATE_TOO_LARGE"
    with pytest.raises(TemplateRegistryError) as partial_error:
        create(partials=(("p.jinja", "four"),), rules=rules)
    assert partial_error.value.code == "JINJA_TEMPLATE_TOO_LARGE"


def test_partial_count_and_total_size_limits_are_enforced() -> None:
    with pytest.raises(TemplateRegistryError):
        create(
            partials=(("a.jinja", "a"), ("b.jinja", "b")),
            rules=JinjaEngineRules(max_partial_count=1),
        )
    with pytest.raises(TemplateRegistryError):
        create(
            partials=(("a.jinja", "aa"), ("b.jinja", "bb")),
            rules=JinjaEngineRules(max_partial_bytes=3),
        )
