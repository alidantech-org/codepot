"""Panel helpers."""

from rich.panel import Panel


def make_summary_panel(title: str, body: str) -> Panel:
    return Panel.fit(body, title=title, border_style="blue")
