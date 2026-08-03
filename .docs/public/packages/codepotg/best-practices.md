---
title: Best practices and troubleshooting
description: Design maintainable packs, test generation, diagnose source and context issues, and upgrade safely.
product: codepotg
package: codepotg
order: 18
---

# Best practices and troubleshooting

## Start from a real project

A useful template pack captures conventions that already work:

- folder layout;
- framework modules;
- naming and exports;
- validation and error handling;
- API client patterns;
- persistence and relation style;
- tests and documentation.

Avoid designing a universal pack before one target architecture is proven.

## Keep concerns separate

- OpenAPI and `x-codegen` describe software intent.
- Normalization provides stable generator facts.
- `paths.yaml` selects and schedules files.
- Jinja renders target syntax.
- lifecycle policy controls project ownership.
- commands perform reviewed project tooling.

Do not hide selection, cleanup, or shell behavior inside templates.

## Prefer normalized variables

Use normalized properties and derived views before `extensions` or `raw`. This keeps packs compatible across OpenAPI 3.0/3.1 and compiler changes.

## Test paths first

```bash
codepotg paths ./templates/typescript
```

Resolve selection, provider, cycle, barrel, and output-path issues before debugging Jinja.

## Dry-run every change

```bash
codepotg generate sdk --dry-run --verbose
```

Review newly created, updated, removed, immutable, and refused files.

## Keep generated roots narrow

Good:

```text
src/generated/api
```

Risky:

```text
src
project root
```

Managed and clean roots should never include unrelated developer-owned files.

## Test packs

A pack test should verify:

- expected output paths;
- exact important file contents;
- stable imports and exports;
- lifecycle mode;
- no duplicate paths;
- no unresolved dependencies;
- behavior with optional metadata absent;
- representative OpenAPI 3.0 and 3.1 inputs where supported.

## Diagnose common failures

### `Codepotg.yaml` not found

Run from the config directory or pass:

```bash
codepotg generate sdk --config path/to/Codepotg.yaml
```

### Legacy config rejected

Rename or recreate `CodepotFile.yml` as `Codepotg.yaml` only when it is intended for the Python generator. The two formats are not interchangeable.

### Unknown language

Use a bundled adapter name or install/register the project-supported adapter. A template directory does not replace the language adapter.

### Template variable missing

- Confirm the emission selection alias.
- Confirm the value is global or supplied by a provider.
- Inspect the variable reference.
- Use a debug template or debug pack.
- Do not switch immediately to `api.raw`.

### Duplicate output path

Two emissions or selected items resolved to the same file. Fix the path expression, grouping key, or selection identity.

### Refused write

Review managed, immutable, protected, output, and clean roots. Do not broaden roots until the calculated path is proven correct.

### Import missing

Use planned dependency/provider facts. Ensure the referenced schema or entity is part of a scheduled emission and exposes the expected provided name/path.

### YAML generation uses high memory

Prefer canonical JSON for large contracts and reuse the cached YAML conversion. Profile the input path before changing template logic.

## Upgrade discipline

Before upgrading CodepotG or a template pack:

1. read the changelog;
2. run pack tests;
3. inspect `codepotg paths`;
4. run a verbose dry run;
5. review output diffs;
6. apply generation without refresh first;
7. use refresh only after cleanup changes are understood.

## Source-control policy

If generated files are committed, require deterministic diffs and code review. If ignored, ensure builds can reproduce them from pinned package and pack versions.

## Security

- Review before/after commands.
- Do not run untrusted templates on a shared server without isolation.
- Do not expose arbitrary filesystem roots.
- Keep raw source values out of output paths unless safely normalized.
- Treat generated code as code that must be reviewed and tested.