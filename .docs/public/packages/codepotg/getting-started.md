---
title: Getting started with codepotg
description: Install CodepotG, create Codepotg.yaml, preview a task, and generate files safely.
product: codepotg
package: codepotg
order: 2
---

# Getting started

## Install

```bash
python -m pip install codepotg
```

Verify the installation:

```bash
codepotg --version
codepotg --help
python -m codepotg --version
```

## Create a project configuration

```bash
codepotg init --yes
```

CodepotG uses `Codepotg.yaml` or `Codepotg.yml`.

```yaml
allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    output: ./generated/sdk
```

`allow: true` is mandatory. It is an explicit acknowledgement that generation may write files and run configured commands.

`CodepotFile.yml` and `CodepotFile.yaml` belong to the TypeScript `codepotx` workflow and are rejected by CodepotG.

## Preview the task

```bash
codepotg generate sdk --dry-run --verbose
```

A dry run resolves input, templates, selections, output paths, lifecycle modes, cleanup plans, and commands without writing files or executing commands.

Review:

- selected language and template directory;
- planned managed and immutable files;
- refused unsafe paths;
- cleanup paths;
- diagnostics and unresolved references.

## Generate

```bash
codepotg generate sdk
```

Run every task in file order:

```bash
codepotg generate --all
```

## Use a custom template pack

```yaml
allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    templateDir: ./templates/typescript
    output: ./generated/sdk
```

A custom pack normally contains:

```text
templates/typescript/
├── paths.yaml
├── models/
│   └── model.ts.j2
├── services/
│   └── service.ts.j2
└── partials/
```

## Inspect a pack before generation

```bash
codepotg paths ./templates/typescript
```

The command reports templates, import strategy, lifecycle defaults, selections, emissions, providers, and barrels.

## Typical development loop

```bash
codepotg paths ./templates/typescript
codepotg generate sdk --dry-run --verbose
codepotg generate sdk
```

## Python API

```python
from pathlib import Path
from codepotg import GeneratorApp

app = GeneratorApp()
result = app.generate(
    config_path=Path('Codepotg.yaml'),
    task_name='sdk',
    dry_run=True,
    verbose=True,
)
```

Use the application API when another Python tool owns orchestration. CLI and API calls use the same runtime workflow.

## Next steps

- [Architecture](/docs/packages/codepotg/architecture)
- [Configuration](/docs/packages/codepotg/configuration)
- [Template packs](/docs/packages/codepotg/template-packs)
- [Lifecycle safety](/docs/packages/codepotg/lifecycle-safety)