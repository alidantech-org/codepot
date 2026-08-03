from __future__ import annotations

from io import BytesIO, TextIOWrapper

from dryv.api import OperationResult, OperationStatus
from rich.console import Console

from dryv_cli.presentation.results import (
    render_cancelled,
    render_failure,
    render_operation,
)


def test_human_output_is_safe_for_windows_cp1252_pipes() -> None:
    buffer = BytesIO()
    stream = TextIOWrapper(buffer, encoding="cp1252", errors="strict")
    console = Console(
        file=stream,
        color_system=None,
        force_terminal=False,
        highlight=False,
        width=120,
    )

    render_operation(
        console,
        OperationResult(
            status=OperationStatus.READY,
            operation_id="0123456789abcdef",
        ),
    )
    render_failure(console, "failed safely", code="CLI_TEST")
    render_cancelled(console, "cancelled safely")
    stream.flush()

    output = buffer.getvalue().decode("cp1252")
    assert "OK ready  operation 0123456789" in output
    assert "X CLI_TEST  failed safely" in output
    assert "- cancelled safely" in output
    assert output.isascii()
