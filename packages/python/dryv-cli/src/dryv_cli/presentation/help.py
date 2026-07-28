from __future__ import annotations

import click


class TreeHelpCommand(click.Command):
    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        _write_command_heading(self, formatter)
        formatter.write_usage(ctx.command_path, " ".join(self.collect_usage_pieces(ctx)))
        if self.help:
            formatter.write_paragraph()
            formatter.write_text(self.help)
        _write_options(self, ctx, formatter)


class TreeHelpGroup(click.Group):
    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        formatter.write(click.style("Dryv", fg="cyan", bold=True))
        formatter.write("\n")
        if self.help:
            formatter.write_text(self.help)
        formatter.write_paragraph()
        formatter.write_usage(ctx.command_path, "[OPTIONS] COMMAND [ARGS]...")

        commands = self.list_commands(ctx)
        if commands:
            formatter.write_paragraph()
            formatter.write(click.style("Commands", fg="cyan", bold=True))
            formatter.write("\n")
            visible = tuple(
                (name, command)
                for name in commands
                if (command := self.get_command(ctx, name)) is not None and not command.hidden
            )
            for index, (name, command) in enumerate(visible):
                branch = "└─" if index == len(visible) - 1 else "├─"
                label = click.style(name, fg="bright_cyan", bold=True)
                description = command.get_short_help_str(limit=60)
                formatter.write(f"  {branch} {label}  {description}\n")

        _write_options(self, ctx, formatter)


def _write_command_heading(command: click.Command, formatter: click.HelpFormatter) -> None:
    formatter.write(click.style(command.name or "command", fg="cyan", bold=True))
    formatter.write("\n")


def _write_options(
    command: click.Command,
    ctx: click.Context,
    formatter: click.HelpFormatter,
) -> None:
    records = tuple(
        record
        for parameter in command.get_params(ctx)
        if (record := parameter.get_help_record(ctx)) is not None
    )
    if not records:
        return
    formatter.write_paragraph()
    formatter.write(click.style("Options", fg="cyan", bold=True))
    formatter.write("\n")
    formatter.write_dl(records)
