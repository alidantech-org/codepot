# CodepotG

**CodepotG** is the stable Python and Jinja generation runtime for turning OpenAPI documents into project-ready source code.

Version **1.0.0** preserves the established Python generator for teams that already use OpenAPI, Jinja template packs, and `CodepotFile.yml`. New Codepot authoring can happen in `codepotx`; when `codepotx` emits OpenAPI, the resulting JSON or YAML document can continue through CodepotG without changing the Python generation workflow.

## What CodepotG provides

- OpenAPI JSON and YAML loading;
- inference and normalized generation contracts;
- Jinja template packs with reusable partials and filters;
- config-driven generation through `CodepotFile.yml`;
- built-in TypeScript, Next.js, Dart, and debug template packs;
- managed and immutable write modes;
- guarded cleanup, dry runs, before/after commands, and structured diagnostics;
- explicit `x-codegen` metadata support for resources, DTOs, entities, access, frontends, screens, and documentation information.

## Requirements

- Python 3.11 or newer;
- an OpenAPI document containing `openapi` and `paths`;
- a CodepotG template pack, either bundled or project-owned.

## Installation

```bash
python -m pip install codepotg
```

Verify the installed release:

```bash
codepotg --version
codepotg --help
```

You can also run the CLI as a Python module:

```bash
python -m codepotg --help
```

## Quick start

Create a `CodepotFile.yml` in the project that owns the generated output:

```yaml
allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    templateDir: ./templates/typescript
    output: ./generated/sdk

    after:
      - run: npx prettier --write generated/sdk
        optional: true
```

Preview the task without modifying files or running real shell commands:

```bash
codepotg generate sdk --dry-run --verbose
```

Generate the files:

```bash
codepotg generate sdk
```

Run every configured task:

```bash
codepotg generate --all
```

## Using OpenAPI emitted by CodepotX

CodepotG remains intentionally OpenAPI-driven. The compatibility flow is:

```text
codepotx.config.ts
        ↓
CodepotX authoring artifact
        ↓
OpenAPI JSON or YAML output
        ↓
CodepotG + Jinja template pack
        ↓
generated project files
```

Point the CodepotG task `input` field at the OpenAPI file emitted by CodepotX:

```yaml
allow: true

tasks:
  legacy-python-generation:
    input: ./.codepot/openapi.json
    language: next
    templateDir: ./templates/next
    output: ./src/generated
```

The first compatibility target is standard OpenAPI **3.0.3** and **3.1.0** documents. Codepot-specific behavior is carried through optional `x-codegen` extensions; ordinary OpenAPI fields remain usable without those extensions.

The post-release compatibility gate will run a real CodepotX-emitted document through CodepotG generation and record any projection changes required on the CodepotX OpenAPI target.

## CodepotFile reference

A task supports:

| Field | Purpose |
| --- | --- |
| `input` | OpenAPI JSON or YAML file |
| `language` | Generation adapter such as `typescript`, `next`, `dart`, or `debug` |
| `templateDir` / `templates` | Jinja template-pack directory |
| `output` | Generated output root |
| `clean` | Paths eligible for guarded refresh cleanup |
| `before` | Commands run before generation |
| `after` | Commands run after generation |
| `env` | Task environment values |
| `frontend` | Optional explicit frontend selection |

`allow: true` is mandatory. CodepotG refuses project generation without that explicit opt-in.

## Frontend metadata

When the document contains `x-codegen.frontends`, a task can select one frontend:

```yaml
frontend: admin
```

Use `frontend: "*"` to expose all authored frontends. CodepotG does not invent screens or components; templates receive only explicitly authored frontend metadata.

## Template packs

A template pack contains Jinja templates and a `paths.yaml` file. Path configuration controls:

- which contract collection a template iterates over;
- output folder and file expressions;
- raw/static files;
- managed or immutable lifecycle behavior;
- protected and clean roots.

Example lifecycle policy:

```yaml
write_policy:
  default_mode: managed
  managed_roots:
    - generated
  immutable_roots:
    - src
  protected_roots:
    - src
  clean_roots:
    - generated

folders:
  generated:
    mode: managed
    parts: [generated]

  scaffold:
    mode: immutable
    parts: [src]
```

Managed files can be updated only inside managed roots. Immutable files are created once and then preserved. Unsafe writes and cleanup operations are refused.

## Python API

```python
from pathlib import Path

from codepotg import GeneratorApp

app = GeneratorApp()
result = app.generate(
    config_path=Path("CodepotFile.yml"),
    task_name="sdk",
    dry_run=True,
    verbose=True,
)

for task in result.tasks:
    print(task.name, task.planned, task.written, task.updated)
```

## Local development

From `packages/python/codepotg`:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
```

On Linux or macOS, activate with:

```bash
source .venv/bin/activate
```

## Release validation

The repository includes a release checker that:

1. verifies all version declarations are `1.0.0`;
2. runs tests and linting;
3. builds the source distribution and wheel;
4. validates metadata with Twine;
5. inspects required wheel modules and bundled templates;
6. installs the wheel into a clean virtual environment;
7. starts both `codepotg --version` and `codepotg --help`.

```bash
python scripts/release.py check
```

Publishing reads `PUBLISH_TOKEN` from the process environment or the ignored local `.env` file. The token is never printed by the release script:

```bash
python scripts/release.py publish
```

PyPI versions are immutable. Validate the exact `1.0.0` artifacts before uploading them.

## Security

- Never commit `.env` or a PyPI token.
- Prefer a project-scoped PyPI token where possible.
- Review every configured `before` and `after` command before running generation.
- Use `--dry-run` when reviewing a new OpenAPI document or template pack.

## License

MIT © 2026 Alidantech.
