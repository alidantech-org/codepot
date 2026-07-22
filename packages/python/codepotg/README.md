codepotg
========

> [!WARNING]
> `codepotg` is deprecated and no longer receives new features. It remains available for existing Python and Jinja generation workflows and as a behavioral reference while generation is rebuilt in the Node.js `codepotx` package.

Config-driven OpenAPI code generation for TypeScript, Dart, Next.js, and debug output.

Installation
------------

```bash
pip install codepotg
```

CLI Usage
---------

`codepotg` exposes one public workflow: `generate`.

Run generation from a project-local `CodepotFile.yml` or `CodepotFile.yaml`:

```bash
codepotg generate
```

Run one named task:

```bash
codepotg generate my-task
```

Run every configured task:

```bash
codepotg generate --all
```

Preview without writing files or running configured shell commands:

```bash
codepotg generate my-task --dry-run --verbose
```

CodepotFile
-----------

Example `CodepotFile.yml`:

```yaml
allow: true

tasks:
  my-task:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates/next
    output: ./lib

    before:
      - run: pnpm exec codepot-openapi generate

    after:
      - run: pnpm prettier --write lib
```

Frontend Tasks
--------------

If the OpenAPI document includes explicit `x-codegen.frontends`, a task can
select one frontend by name:

```yaml
tasks:
  admin-frontend:
    input: ./openapi.yaml
    language: typescript
    templateDir: ./templates/next
    output: ../admin
    frontend: admin
```

Use `frontend: "*"` to expose every authored frontend. If `frontend` is omitted,
old backend/API generation behavior is unchanged. `codepotg` does not infer
screens from resources or operations; templates only see explicitly authored
frontend components and screens.

Frontend-aware templates can select:

```yaml
folders:
  frontend_screens:
    mode: immutable
    select: selected_frontend.screens
    as: screen
    parts: [src, screens]
```

Info Metadata
-------------

`x-codegen.info` metadata is preserved for templates on operations, entities,
frontends, screens, and components. The `info_comment` Jinja filter can render
normalized info categories into comment body lines:

```jinja
/**
{{ operation.meta.info | info_comment }}
 */
```

Template Write Safety
---------------------

Templates can opt into lifecycle-aware writes with `write_policy` in `paths.yaml`.
Without `write_policy`, existing templates keep the old behavior.

```yaml
write_policy:
  default_mode: managed
  managed_roots:
    - gen
  immutable_roots:
    - src
  protected_roots:
    - src
  clean_roots:
    - gen

folders:
  generated:
    mode: managed
    parts: [gen]

  scaffold:
    mode: immutable
    parts: [src]
```

`managed` files may be created or updated, but only under `managed_roots`.
`immutable` files are created once and skipped when they already exist. `mode:
once` is accepted as an alias for `immutable` when `write_policy` is present.
Unsafe writes are refused and fail the task instead of being written.

`codepotg generate --refresh` cleans only paths allowed by `clean_roots` and
will not delete immutable roots.

Local Development
-----------------

Install this checkout in editable mode:

```bash
python -m pip install -e .
codepotg --help
```

Build And Publish
-----------------

Install build tools:

```bash
python -m pip install build twine
```

Build locally:

```bash
python -m build
```

Check the package:

```bash
python -m twine check dist/*
```

Publish to PyPI:

```bash
python -m twine upload dist/*
```
