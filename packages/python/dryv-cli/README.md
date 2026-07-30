# dryv-cli

`dryv-cli` is the terminal frontend for the reusable `dryv` runtime.

It owns command parsing, colors, spinners, interactive confirmation, trees, summaries, diagnostics, machine JSON, and exit-code policy. It contains no semantic, planning, rendering, plugin-discovery, or writer implementation.

## Install

```bash
python -m pip install -e ../dryv
python -m pip install -e .
```

## Commands

```text
dryv
├── plan       validate and inspect a complete artifact plan
├── generate   render to memory or write managed files
└── plugins    inspect the loaded runtime plugin graph
```

Examples:

```bash
dryv plan dryv.yaml
dryv plan dryv.yaml --json
dryv generate dryv.yaml --memory
dryv generate dryv.yaml --destination ./generated
dryv generate dryv.yaml --destination ./generated --yes
dryv plugins
dryv plugins --json
```

## Write confirmation

In an interactive terminal, managed generation shows the plan and asks before writing. Use `--yes` to skip that confirmation.

```bash
dryv generate dryv.yaml --yes
```

Automation and JSON runs never prompt. `--confirm` may be used to require a prompt explicitly; it fails clearly when no TTY is available rather than hanging.

## UX rules

- Rich owns terminal output, semantic colors, trees, summaries, and loading indicators.
- Questionary owns intentional interactive confirmation.
- Click owns command parsing and help dispatch.
- Python `print()` and `input()` are prohibited.
- Panels and box borders are prohibited.
- Hierarchical information uses readable `├─` / `└─` trees.
- Machine output uses `--json`, contains no ANSI color, and never prompts.
- Commands consume only public `dryv` runtime contracts.

## Source structure

```text
src/dryv_cli/
├── commands/
│   ├── common.py
│   ├── generate.py
│   ├── plan.py
│   └── plugins.py
├── presentation/
│   ├── console.py
│   ├── diagnostics.py
│   ├── help.py
│   ├── results.py
│   ├── serialization.py
│   ├── theme.py
│   └── trees.py
├── prompts/
│   └── confirm.py
├── services/
│   ├── exit_codes.py
│   └── runtime.py
├── app.py
├── main.py
└── __main__.py
```

There are no placeholder `.gitkeep` files in implemented directories.

## Verification

```bash
python -m pip install -e "../dryv[dev]"
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build
```
