# CodepotG

**CodepotG** is the supported Python and Jinja template-pack manager and generation runtime for turning OpenAPI documents into project-ready source code.

Version **1.0.0** is the first stable PyPI release of the mature generator used by the original Codepot workflow. It consumes OpenAPI produced by `codepot-openapi` or another compatible source, performs inference into normalized generation contracts, and renders bundled or project-owned Jinja template packs.

CodepotG remains active and supported while the official `codepotx` runtime is developed. It is not deprecated.

## Installation

```bash
python -m pip install codepotg
```

- documentation: https://code.alidantech.org/docs/packages/codepotg
- PyPI: https://pypi.org/project/codepotg/
- source: https://github.com/alidantech-org/codepot/tree/main/packages/python/codepotg

The complete documentation covers configuration, tasks, CLI commands, template packs, `paths.yaml`, Jinja templates, every normalized variable domain, lifecycle safety, OpenAPI preservation, performance, and best practices.

Requirements:

- Python 3.11 or newer;
- OpenAPI 3.0 or 3.1 JSON/YAML containing `openapi` and `paths`;
- a bundled language pack or project-owned Jinja template pack.

## What CodepotG provides

- streamed JSON input through an indexed JSONL cache and cached YAML compatibility conversion;
- normalized inference for resources, operations, schemas, entities, access, frontends, and documentation;
- Jinja templates, partials, filters, and both legacy-folder and selection-graph `paths.yaml` planning;
- bundled TypeScript, Next.js, Dart, and debug template packs;
- custom project-owned template directories;
- managed and immutable file modes;
- guarded cleanup, dry runs, before/after commands, and structured diagnostics;
- bounded graph render contexts, explicit dependency providers, barrels, lazy source resolvers, and atomic writes;
- optional memory-stage tracing for generation diagnostics;
- support for optional `x-codegen` metadata emitted by `codepot-openapi`.

## Quick start

Create a configuration:

```bash
codepotg init --yes
```

`Codepotg.yaml`:

```yaml
allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    output: ./generated/sdk
```

Preview:

```bash
codepotg generate sdk --dry-run --verbose
```

Generate:

```bash
codepotg generate sdk
```

Run every configured task:

```bash
codepotg generate --all
```

`allow: true` is mandatory. CodepotG intentionally uses `Codepotg.yaml`; the TypeScript runtime uses `CodepotFile.yml`.

## Custom template packs

```yaml
allow: true

tasks:
  custom-sdk:
    input: ./openapi.json
    language: typescript
    templateDir: ./templates/typescript
    output: ./generated/sdk
```

A pack contains Jinja templates and `paths.yaml`. It can control selectors, aliases, output paths, raw files, managed or immutable lifecycles, protected roots, and clean roots.

New packs can use named `selections`, `emissions`, and `barrels`. Legacy `folders` packs remain supported while projects migrate. Graph packs receive bounded globals, their declared selection, explicit provider outputs, and lazy JSONL-backed resolvers rather than a copied full source document.

## Performance and memory tracing

JSON input is indexed through a streaming JSONL path. YAML remains supported through a cached canonical JSON conversion. Diagnose a pipeline with:

```bash
python scripts/profile_memory.py tests/fixtures/openapi.json --full --emit --json
```

Normal generation can record stage snapshots with `CODEPOTG_MEMORY_TRACE` and `CODEPOTG_MEMORY_TRACE_FILE`. See `docs/performance-memory.md` for metric interpretation.

## Prototype workflow

```text
codepot-openapi
    ↓ OpenAPI 3.1 JSON/YAML + optional x-codegen
codepotg
    ↓ normalized inference + Jinja template packs
generated application, SDK, UI, or documentation files
```

Standard OpenAPI works without Codepot extensions. `x-codegen` preserves richer semantics when they are available.

## Relationship to codepotx

`codepotx` is the official JavaScript runtime rewrite. CodepotG remains the mature supported generator while equivalent capabilities are validated, redesigned, and stabilized in that runtime. Existing users do not need to migrate merely because the rewrite is in progress.

## Python API

```python
from pathlib import Path
from codepotg import GeneratorApp

app = GeneratorApp()
result = app.generate(
    config_path=Path("Codepotg.yaml"),
    task_name="sdk",
    dry_run=True,
    verbose=True,
)
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
```

On Git Bash for Windows, activate with `source .venv/Scripts/activate`.

Release validation:

```bash
python scripts/release.py check
```

## Security

- Never commit `.env` files or publishing tokens.
- Review configured `before` and `after` commands.
- Use `--dry-run` before applying a new contract or template pack.
- Keep managed, immutable, protected, and clean roots narrow.

## License

MIT © 2026 Alidantech
