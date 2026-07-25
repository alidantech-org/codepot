---
title: Lifecycle, cleanup, and write safety
description: Configure managed and immutable files, protected roots, clean roots, dry runs, commands, and atomic writes.
product: codepotg
package: codepotg
order: 16
---

# Lifecycle, cleanup, and write safety

CodepotG plans lifecycle behavior before writing. A template pack must define where generated ownership is allowed.

## Lifecycle modes

### Managed

Managed files are owned by the generator inside configured managed roots. They may be created, updated, or removed as stale when the plan and cleanup policy permit it.

### Immutable

Immutable files are created only when absent. Existing files are preserved so developers can own or extend them after initial generation.

Use immutable mode for bootstrap files that should not be overwritten.

## Write policy

```yaml
write_policy:
  default_mode: managed
  managed_roots:
    - generated
  immutable_roots:
    - src/bootstrap
  protected_roots:
    - src
  clean_roots:
    - generated
```

### `managed_roots`

Only paths inside these roots may receive managed updates.

### `immutable_roots`

Immutable emissions must remain inside these roots when configured.

### `protected_roots`

Protected roots refuse unsafe managed writes or cleanup even when a template calculates a matching path.

### `clean_roots`

Refresh cleanup is restricted to these roots and known generated ownership.

## Task cleanup

A task can define explicit clean paths:

```yaml
tasks:
  sdk:
    clean:
      - ./generated/sdk
```

Cleanup runs only with refresh behavior:

```bash
codepotg generate sdk --refresh
```

Do not list broad application roots. Keep clean paths as narrow as the generated output.

## Dry runs

```bash
codepotg generate sdk --dry-run --verbose
```

A dry run:

- resolves source and templates;
- builds selections and dependencies;
- plans outputs and cleanup;
- renders planned content where required for validation;
- reports commands;
- does not write files;
- does not execute commands.

Dry runs are the required review step for new or changed packs.

## Refused writes

CodepotG reports paths that violate lifecycle or root policy as refused. A refused path is not silently redirected.

Common causes:

- output escapes the task root;
- managed file targets an immutable or protected root;
- path expression contains unsafe traversal;
- duplicate emissions claim one path with conflicting lifecycle;
- cleanup targets an unowned path.

## Atomic writes

Generated content is staged before replacing a managed file. This reduces partial-file states when a process is interrupted.

The generation report distinguishes created, updated, unchanged, skipped, refused, and immutable outcomes.

## Commands

Before and after commands are executable project code.

```yaml
after:
  - name: Format generated output
    run: pnpm prettier --write generated
```

Controls:

```bash
codepotg generate sdk --skip-before
codepotg generate sdk --skip-after
```

Dry runs skip all commands.

Use optional commands only when failure truly should not invalidate generation.

## Refresh discipline

A safe refresh workflow is:

```bash
codepotg generate sdk --dry-run --verbose
codepotg generate sdk --refresh --verbose
```

Review planned cleanup before applying it.

## Source control

Generated files can be committed or ignored according to project policy. Lifecycle safety still matters in both cases:

- committed output needs reviewable diffs;
- ignored output needs deterministic recreation;
- immutable bootstrap files should become clearly developer-owned;
- manifests and caches should not be confused with public generated source.

## Security guidance

- Keep `allow: true` visible in reviewed project configuration.
- Review every new template pack and command.
- Never allow user-submitted template packs to run in an unsandboxed server process.
- Keep output, managed, protected, and clean roots narrow.
- Do not use raw OpenAPI values directly in paths without safe normalization.