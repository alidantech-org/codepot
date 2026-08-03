from __future__ import annotations

from collections.abc import Callable, Iterable

import pytest

from dryv.api import CancellationToken
from dryv.ports import RenderRequest, RenderResult
from dryv_template_jinja import JinjaTemplateEngine

RenderHelper = Callable[..., RenderResult]
DiagnosticCodeHelper = Callable[[RenderResult], str]


@pytest.fixture
def engine() -> JinjaTemplateEngine:
    return JinjaTemplateEngine()


@pytest.fixture
def render() -> RenderHelper:
    return _render


@pytest.fixture
def diagnostic_code() -> DiagnosticCodeHelper:
    return _diagnostic_code


def _render(
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


def _diagnostic_code(result: RenderResult) -> str:
    assert result.content is None
    assert result.diagnostics.has_errors
    return result.diagnostics.errors[0].code
