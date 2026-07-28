from __future__ import annotations

from collections.abc import Iterable

import pytest

from dryv.api import CancellationToken
from dryv.ports import RenderRequest, RenderResult
from dryv_template_jinja import JinjaTemplateEngine


@pytest.fixture
def engine() -> JinjaTemplateEngine:
    return JinjaTemplateEngine()


def render(
    engine: JinjaTemplateEngine,
    source: str,
    *,
    template_id: str = "root.jinja",
    context: Iterable[tuple[str, object]] = (),
    partials: Iterable[tuple[str, str]] = (),
    cancellation: CancellationToken | None = None,
) -> RenderResult:
    return engine.render(
        RenderRequest(
            template_id=template_id,
            source=source,
            context=tuple(context),
            partials=tuple(partials),
        ),
        cancellation or CancellationToken(),
    )


def diagnostic_code(result: RenderResult) -> str:
    assert result.content is None
    assert result.diagnostics.has_errors
    return result.diagnostics.errors[0].code
