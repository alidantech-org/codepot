from __future__ import annotations

from io import StringIO

from rich.console import Console

from dryv_cli.presentation.results import render_json


def test_json_output_contains_no_ansi_even_on_a_color_terminal() -> None:
    stream = StringIO()
    console = Console(file=stream, force_terminal=True, color_system="standard")

    render_json(console, {"status": "ready", "value": "example"})

    output = stream.getvalue()
    assert "\x1b[" not in output
    assert '"status": "ready"' in output
    assert '"value": "example"' in output
