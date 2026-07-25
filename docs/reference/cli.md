---
title: CLI reference
description: Compare the commands exposed by codepot-openapi, codepotg, codepotx-cli, and the final codepot CLI.
order: 50
---

# CLI reference

Codepot currently has several commands because each implementation layer has a distinct role.

## `codepot-openapi`

TypeScript contract builder and OpenAPI emitter:

```bash
codepot-openapi init
codepot-openapi generate
codepot-openapi validate
```

## `codepotg`

Python and Jinja generator:

```bash
codepotg init --yes
codepotg task add <name> --language <language> --input <file> --output <dir> --yes
codepotg generate <task>
codepotg generate <task> --dry-run --verbose
codepotg generate --all
codepotg generate <task> --refresh
codepotg generate <task> --skip-before --skip-after
codepotg --version
```

Configuration: `Codepotg.yaml`.

## `codepotx`

JavaScript runtime frontend provided by `codepotx-cli`:

```bash
codepotx validate
codepotx inspect --json
codepotx variables <task>
codepotx plan <task> --json
codepotx generate <task> --dry-run
codepotx generate <task>
codepotx features
codepotx version
codepotx help
```

Common options:

```text
-r, --root <path>
-f, --file <path>
-c, --config <path>
-t, --task <name>
    --all
    --dry-run
    --refresh
    --skip-before
    --skip-after
    --json
    --pretty
-v, --verbose
```

Configuration: `codepotx.config.ts` and `CodepotFile.yml`.

## Final `codepot` CLI

Rust language and platform command:

```bash
codepot check
codepot check --format json
codepot format
codepot format --check
codepot compile
codepot inspect modules
codepot inspect imports <file>
codepot inspect symbols
codepot inspect ast <file>
codepot inspect ir <file>
codepot doctor
codepot lsp --stdio
```

Configuration: `Codepot.toml`.

## Command-name rule

- `codepot-openapi` belongs to the TypeScript OpenAPI prototype.
- `codepotg` belongs to the Python generator.
- `codepotx` belongs to the official JavaScript runtime release line.
- `codepot` is the final platform CLI command.
