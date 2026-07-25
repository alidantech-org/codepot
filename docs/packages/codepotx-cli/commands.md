---
title: Command reference
description: Reference the validate, inspect, variables, plan, generate, features, help, and version commands exposed by codepotx-cli.
product: codepotx-cli
---

# Command reference

## `validate`

```bash
codepotx validate
```

Loads the project through the runtime and validates configuration, authoring, template packs, tasks, sources, variables, and compatibility boundaries. It does not generate files.

Use `--json` for machine-readable diagnostics.

## `inspect`

```bash
codepotx inspect
codepotx inspect --json --pretty
```

Returns an inspectable view of the resolved Codepot project. The runtime owns the exact response shape; the CLI only formats it.

## `variables`

```bash
codepotx variables <task>
codepotx variables sdk --json --pretty
```

Returns the template-variable catalog available to the selected task. Use it to document a pack, power editor suggestions, or diagnose missing variables.

A positional task name is accepted where a command requires one.

## `plan`

```bash
codepotx plan <task>
codepotx plan sdk --json --pretty
```

Produces a deterministic generation plan without writing files. The plan describes outputs, lifecycle modes, dependencies, commands, cleanup actions, refusals, and diagnostics.

## `generate`

```bash
codepotx generate <task>
codepotx generate sdk --dry-run
codepotx generate --all
```

Executes one task or all tasks through the runtime.

Useful controls:

```bash
codepotx generate sdk --refresh
codepotx generate sdk --skip-before
codepotx generate sdk --skip-after
codepotx generate sdk --verbose
```

`--dry-run` renders without writes, cleanup, or commands.

## `features`

```bash
codepotx features
codepotx features --json
```

Reports runtime and package feature information suitable for compatibility checks and user interfaces.

## `help`

```bash
codepotx help
codepotx help generate
```

Displays command usage. Help output is presentation owned by the CLI; domain documentation remains in the package docs and runtime contracts.

## `version`

```bash
codepotx version
```

Reports CLI version information. Project operations may still use the compatible project-local runtime version selected by the consumer project.

## Exit behavior

The CLI converts typed runtime results into process exit codes. Validation failures, unresolved project configuration, invalid arguments, and failed required generation steps produce non-zero exits. Informational warnings should remain distinguishable from failures in JSON output.

## Related pages

- [Options](/docs/packages/codepotx-cli/options)
- [Automation](/docs/packages/codepotx-cli/automation)
- [Generation with codepotx](/docs/packages/codepotx/generation)
