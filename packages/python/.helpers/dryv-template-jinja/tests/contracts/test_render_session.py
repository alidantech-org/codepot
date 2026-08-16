from __future__ import annotations

from dataclasses import dataclass

from dryv_template_jinja import JinjaRenderSession


@dataclass(frozen=True)
class Output:
    id: str
    path: str


@dataclass(frozen=True)
class Request:
    job_id: str
    template_content: bytes
    context: dict[str, object]
    outputs: tuple[Output, ...]


def test_jinja_render_session_is_structurally_protocol_compatible() -> None:
    session = JinjaRenderSession(max_concurrency=2)
    hello = session.hello()
    assert hello.capabilities == ("jinja/v1",)
    assert hello.max_concurrency == 2
    assert hello.deterministic

    result = session.render(
        Request(
            "job.user",
            b"export interface {{ schema.name }} {}\n",
            {"schema": {"name": "User"}},
            (Output("artifact.user", "src/user.ts"),),
        )
    )
    assert not result.cancelled
    assert result.outputs[0].id == "artifact.user"
    assert result.outputs[0].content == b"export interface User {}\n"
    assert result.outputs[0].content_hash.startswith("sha256:v1:artifact-content:")


def test_jinja_render_session_reports_strict_undefined_errors() -> None:
    session = JinjaRenderSession()
    result = session.render(
        Request(
            "job.bad",
            b"{{ missing.value }}",
            {},
            (Output("artifact.bad", "bad.txt"),),
        )
    )
    assert result.outputs == ()
    assert result.diagnostics[0].code == "JINJA_RENDER_FAILED"


def test_jinja_render_session_cancellation_is_protocol_visible() -> None:
    session = JinjaRenderSession()
    session.cancel("job.cancelled")
    result = session.render(
        Request(
            "job.cancelled",
            b"hello",
            {},
            (Output("artifact.cancelled", "cancelled.txt"),),
        )
    )
    assert result.cancelled
