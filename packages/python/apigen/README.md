codepotx
========

Config-driven OpenAPI code generation for TypeScript, Dart, and debug output.

Installation
------------

```bash
pip install codepotx
```

CLI Usage
---------

`codepotx` exposes one public workflow: `generate`.

Run generation from a project-local `CodepotFile.yml` or `CodepotFile.yaml`:

```bash
codepotx generate
```

Run one named task:

```bash
codepotx generate my-task
```

Run every configured task:

```bash
codepotx generate --all
```

Preview without writing files or running configured shell commands:

```bash
codepotx generate my-task --dry-run --verbose
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

`codepotx generate --refresh` cleans only paths allowed by `clean_roots` and
will not delete immutable roots.

Local Development
-----------------

Install this checkout in editable mode:

```bash
python -m pip install -e .
codepotx --help
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
