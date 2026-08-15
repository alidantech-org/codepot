from __future__ import annotations

from hashlib import sha256

import pytest

from dryv.features.templating import (
    PlannedOutput,
    RenderDiagnostic,
    RenderedOutput,
    RendererHello,
    RenderRequest,
    RenderResult,
    TemplatingError,
    TemplatingFeature,
)


def _hash(content: bytes) -> str:
    return "sha256:" + sha256(content).hexdigest()


class FakeSession:
    def __init__(self, result: RenderResult | None = None) -> None:
        self.cancelled: list[str] = []
        self._result = result

    def hello(self) -> RendererHello:
        return RendererHello("jinja", "1.0.0", ("jinja/v1",), (1,), (1,), ("text/x-jinja-template",), "renderer:jinja:1")

    def render(self, request: RenderRequest) -> RenderResult:
        if self._result is not None:
            return self._result
        content = b"export const value = 1;\n"
        return RenderResult(request.job_id, "renderer:jinja:1", (RenderedOutput("artifact.a", content, _hash(content)),), (RenderDiagnostic("INFO", "ok", "info"),))

    def cancel(self, job_id: str) -> None:
        self.cancelled.append(job_id)


def _request() -> RenderRequest:
    return RenderRequest(1, 1, "job.a", "jinja/v1", "resource://pack/a.jinja", "text/x-jinja-template", b"{{ value }}", "template:hash", {"value": 1}, "context:hash", (PlannedOutput("artifact.a", "src/a.ts"),))


def test_fake_render_session_returns_validated_output() -> None:
    rendered = TemplatingFeature().render(FakeSession(), _request(), content_hash=_hash)
    assert rendered.outputs[0].id == "artifact.a"
    assert rendered.diagnostics[0].severity == "info"


def test_unplanned_output_is_rejected() -> None:
    content = b"bad"
    session = FakeSession(RenderResult("job.a", "renderer:jinja:1", (RenderedOutput("artifact.escape", content, _hash(content)),)))
    with pytest.raises(TemplatingError) as caught:
        TemplatingFeature().render(session, _request(), content_hash=_hash)
    assert caught.value.code == "RENDER_UNKNOWN_OUTPUT"


def test_wrong_job_and_fingerprint_are_rejected() -> None:
    content = b"x"
    with pytest.raises(TemplatingError) as wrong_job:
        TemplatingFeature().render(FakeSession(RenderResult("other", "renderer:jinja:1", (RenderedOutput("artifact.a", content, _hash(content)),))), _request(), content_hash=_hash)
    assert wrong_job.value.code == "RENDER_JOB_MISMATCH"

    with pytest.raises(TemplatingError) as fingerprint:
        TemplatingFeature().render(FakeSession(RenderResult("job.a", "renderer:changed", (RenderedOutput("artifact.a", content, _hash(content)),))), _request(), content_hash=_hash)
    assert fingerprint.value.code == "RENDER_FINGERPRINT_MISMATCH"


def test_pre_cancelled_job_is_not_rendered() -> None:
    session = FakeSession()
    with pytest.raises(TemplatingError) as caught:
        TemplatingFeature().render(session, _request(), content_hash=_hash, is_cancelled=lambda: True)
    assert caught.value.code == "RENDER_CANCELLED"
    assert session.cancelled == ["job.a"]
