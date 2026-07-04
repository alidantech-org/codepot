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
