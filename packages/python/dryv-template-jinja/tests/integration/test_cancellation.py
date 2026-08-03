from __future__ import annotations

from dryv.api import CancellationToken
from dryv_template_jinja import JinjaTemplateEngine


class CheckpointCancellation(CancellationToken):
    def __init__(self, cancel_at: int) -> None:
        super().__init__()
        self._checks = 0
        self._cancel_at = cancel_at

    def raise_if_cancelled(self) -> None:
        self._checks += 1
        if self._checks == self._cancel_at:
            self.cancel("sensitive internal reason")
        super().raise_if_cancelled()


def test_pre_cancelled_request_returns_no_partial_content(render, diagnostic_code) -> None:
    token = CancellationToken()
    token.cancel("stop")
    result = render(JinjaTemplateEngine(), "content", cancellation=token)
    assert diagnostic_code(result) == "JINJA_CANCELLED"
    assert result.content is None


def test_mid_render_cancellation_returns_no_partial_content(render, diagnostic_code) -> None:
    token = CheckpointCancellation(cancel_at=8)
    result = render(
        JinjaTemplateEngine(),
        "{% for item in items %}{{ item }}{% endfor %}",
        context=(("items", tuple(range(100))),),
        cancellation=token,
    )
    assert diagnostic_code(result) == "JINJA_CANCELLED"
    assert result.content is None
    assert "sensitive" not in str(result.diagnostics.errors[0].details)
