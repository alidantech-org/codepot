# CodepotG

**CodepotG** is the stable Python and Jinja generation runtime for turning OpenAPI documents into project-ready source code.

Version **1.0.0** preserves the established Python generator for teams that use OpenAPI, Jinja template packs, and configuration-driven generation. New Codepot authoring can happen in `codepotx`; when CodepotX emits OpenAPI, the resulting JSON or YAML document can continue through CodepotG without changing the Python generation model.

## What CodepotG provides

- OpenAPI 3.0 and 3.1 JSON or YAML loading;
- inference and normalized generation contracts;
- Jinja template packs with reusable partials and filters;
- project tasks configured in `Codepotg.yaml`;
- bundled TypeScript, Next.js, Dart, and debug template packs;
- optional project-owned template packs;
- managed and immutable write modes;
- guarded cleanup, dry runs, before/after commands, and structured diagnostics;
- optional `x-codegen` metadata for resources, DTOs, entities, access, frontends, screens, and documentation.

## Requirements

- Python 3.11 or newer;
- an OpenAPI document containing `openapi` and `paths`;
- either a bundled language pack or a project-owned Jinja template pack.

## Installation

```bash
python -m pip install codepotg
```

Verify the installed release:

```bash
codepotg --version
codepotg --help
python -m codepotg --version
```

## Quick start

Create a starter configuration:

```bash
codepotg init --yes
```

This creates `Codepotg.yaml`:

```yaml
allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    output: ./generated/sdk
```

When `templateDir` is omitted, CodepotG uses the bundled template pack selected by `language`.

Preview without writing files or running real shell commands:

```bash
codepotg generate sdk --dry-run --verbose
```

Generate files:

```bash
codepotg generate sdk
```

Run every configured task:

```bash
codepotg generate --all
```

## Custom template packs

Set `templateDir` only when the project owns a custom pack:

```yaml
allow: true

tasks:
  custom-sdk:
    input: ./openapi.json
    language: typescript
    templateDir: ./templates/typescript
    output: ./generated/sdk
```

The `templates` key is accepted as an alias for `templateDir`.

## `Codepotg.yaml` reference

A task supports:

| Field | Required | Purpose |
| --- | --- | --- |
| `input` | yes | OpenAPI JSON or YAML file |
| `language` | yes | Adapter such as `typescript`, `next`, `dart`, or `debug` |
| `output` | yes | Generated output root |
| `templateDir` / `templates` | no | Custom Jinja template-pack directory; omitted means bundled templates |
| `clean` | no | Paths eligible for guarded refresh cleanup |
| `before` | no | Commands run before generation |
| `after` | no | Commands run after generation |
| `env` | no | Task environment values |
| `frontend` | no | Explicit frontend selection |
| `description` | no | Human-readable task description |

`allow: true` is mandatory. CodepotG refuses project generation without that explicit opt-in.

The Python package intentionally uses `Codepotg.yaml`. `CodepotFile.yml` and `CodepotFile.yaml` belong to the TypeScript Codepot workflow and are rejected by CodepotG to prevent accidental cross-tool configuration.

## Commands

Create the initial config:

```bash
codepotg init --yes
```

Add a task:

```bash
codepotg task add admin-sdk \
  --language next \
  --input ./openapi.json \
  --output ./src/generated \
  --yes
```

Use a non-default config path explicitly:

```bash
codepotg generate sdk --config ./config/codepotg-admin.yaml
```

Refresh only configured safe cleanup paths:

```bash
codepotg generate sdk --refresh
```

Skip configured commands when diagnosing generation:

```bash
codepotg generate sdk --skip-before --skip-after --verbose
```

## Using OpenAPI emitted by CodepotX

CodepotG remains intentionally OpenAPI-driven:

```text
codepotx.config.ts
        ↓
CodepotX authoring artifact
        ↓
OpenAPI 3.0.3 or 3.1.0 JSON/YAML
        ↓
CodepotG + Jinja template pack
        ↓
generated project files
```

Point a CodepotG task at the OpenAPI file emitted by CodepotX:

```yaml
allow: true

tasks:
  sdk:
    input: ./.codepot/openapi.json
    language: next
    output: ./src/generated
```

Standard OpenAPI fields work without Codepot extensions. Optional `x-codegen` data preserves additional Codepot behavior such as resource placement, schema roles, frontend definitions, and normalized documentation metadata.

The compatibility gate validates both OpenAPI **3.0.3** and **3.1.0** documents and will later run a real CodepotX-emitted document through the published CodepotG package.

## Frontend metadata

When the document contains `x-codegen.frontends`, a task can select one frontend:

```yaml
frontend: admin
```

Use `frontend: "*"` to expose all authored frontends. CodepotG does not invent screens or components; templates receive only explicitly authored frontend metadata.

## Template packs

A template pack contains Jinja templates and `paths.yaml`. Path configuration controls:

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
    config_path=Path("Codepotg.yaml"),
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

On Linux or macOS, activate with `source .venv/bin/activate`.

## Release validation

The repository release checker:

1. verifies every version declaration is `1.0.0`;
2. runs tests and Ruff;
3. builds the source distribution and wheel;
4. validates metadata with Twine;
5. inspects required modules, templates, license, and config documentation;
6. installs the wheel into a clean virtual environment;
7. starts `codepotg --version`, `codepotg --help`, and `python -m codepotg`.

```bash
python scripts/release.py check
```

Publishing reads `PUBLISH_TOKEN` from the process environment or ignored local `.env` file. The token is never printed:

```bash
python scripts/release.py publish
```

Do not publish while any release check fails. PyPI versions are immutable.

## Security

- Never commit `.env` or a PyPI token.
- Prefer a project-scoped PyPI token after the project exists.
- Review every configured `before` and `after` command.
- Use `--dry-run` when reviewing a new OpenAPI document or template pack.

## License

MIT © 2026 Alidantech.
