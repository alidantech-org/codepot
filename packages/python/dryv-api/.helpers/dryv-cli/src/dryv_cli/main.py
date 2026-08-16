from __future__ import annotations

from collections.abc import Sequence

import click

from dryv_cli.app import app
from dryv_cli.presentation import get_console, render_cancelled, render_failure


def main(argv: Sequence[str] | None = None) -> int:
    try:
        result = app.main(
            args=list(argv) if argv is not None else None,
            prog_name="dryv",
            standalone_mode=False,
        )
        return result if isinstance(result, int) else 0
    except click.exceptions.Exit as exc:
        return exc.exit_code
    except click.ClickException as exc:
        render_failure(get_console(), exc.format_message(), code="CLI_USAGE_ERROR")
        return exc.exit_code
    except (click.Abort, KeyboardInterrupt):
        render_cancelled(get_console(), "Interrupted.")
        return 130
