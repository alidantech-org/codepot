# dryv-cli

`dryv-cli` is the terminal frontend for the `dryv` runtime.

It contains command parsing, terminal colors, spinners, interactive confirmation, trees, summaries, diagnostic presentation, JSON output, and exit-code policy. It does not contain planning, generation, plugin discovery rules, writer behavior, or semantic logic.

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
dryv generate dryv.yaml --destination ./generated --confirm
dryv generate dryv.yaml --destination ./generated --yes
dryv plugins
```

## UX rules

- Rich owns terminal output and loading indicators.
- Questionary owns intentional interactive prompts.
- Click owns command parsing and help dispatch.
- Python `print()` and `input()` are prohibited.
- Box and panel borders are prohibited.
- Hierarchical information uses readable trees.
- Machine output uses `--json` and never prompts.
- Non-interactive environments never receive a prompt.
- Commands call only the public `dryv` runtime API.

## Source structure

```text
src/dryv_cli/
├── commands/       thin command handlers
├── presentation/   colors, trees, diagnostics, summaries, JSON
├── prompts/        Questionary interactions
├── services/       runtime acquisition
├── app.py          command composition
├── main.py         process entry point and exit handling
└── __main__.py     python -m dryv_cli
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
