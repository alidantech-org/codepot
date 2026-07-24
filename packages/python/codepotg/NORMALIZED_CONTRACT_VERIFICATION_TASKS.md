# CodepotG Normalized Contract Verification Tasks

This file is a mandatory companion to `NORMALIZED_CONTRACT_TASKS.md`.

A normalized-contract task is not complete because a model, property, mapper, or template variable exists. It is complete only when the behavior is observable through committed tests and real generated files.

## Completion rule

Every completed contract task must include all applicable evidence:

- [ ] a focused contract or inference test;
- [ ] a real Jinja `.j2` template that reads the new variable;
- [ ] a project fixture with a real `Codepotg.yaml` or `Codepotg.yml` task;
- [ ] generation through `GeneratorApp.generate` or the public CLI;
- [ ] assertions against emitted file paths and contents;
- [ ] a failure or missing-value scenario;
- [ ] TypeScript verification when the fact is usable by TypeScript;
- [ ] Dart verification when the fact is usable by Dart;
- [ ] a documented command that users can run locally;
- [ ] the related checklist item updated only after the tests pass.

## Fixed project-fixture layout

```text
tests/fixtures/projects/
  typescript/
    Codepotg.yml
    openapi.yaml
    .gitignore
    templates/
      paths.yaml
      multiple focused .j2 templates
  dart/
    Codepotg.yaml
    openapi.yaml
    .gitignore
    templates/
      paths.yaml
      multiple focused .j2 templates
```

Each fixture pack owns one fixed `paths.yaml`. Tests add coverage by adding focused templates, not by replacing the pack layout per test.

Generated output is written beneath `.generated/`. The fixture `.gitignore` must ignore that directory so the same project can be generated manually without polluting Git status.

## Required template coverage

The fixture packs will grow in the same order as the normalized contract:

- [ ] global variables and project metadata;
- [ ] file and emission context;
- [ ] naming variants;
- [ ] resource variables and collections;
- [ ] schema groups and schema identity;
- [ ] fields and primitive constraints;
- [ ] defaults, constants, examples, and explicit null;
- [ ] arrays, objects, composition, and references;
- [ ] operations, parameters, request bodies, responses, and media types;
- [ ] root and operation security;
- [ ] cache read and invalidation rules;
- [ ] access definitions and resolved uses;
- [ ] runtime transport and hooks;
- [ ] sources and query metadata;
- [ ] entities, inherited fields, backend fields, relations, and constraints;
- [ ] frontend definitions, components, screens, and uses;
- [ ] extensions, raw source, diagnostics, and loss reports;
- [ ] imports and dependency planning;
- [ ] safe empty and failure behavior.

## Config compatibility gate

Both standard CodepotG filenames are supported:

```text
Codepotg.yaml
Codepotg.yml
```

Required tests:

- [x] explicit `.yaml` loading;
- [x] explicit `.yml` loading;
- [x] automatic `.yaml` discovery;
- [x] automatic `.yml` discovery;
- [x] ambiguity failure when both files exist;
- [x] legacy `CodepotFile.yml` and `CodepotFile.yaml` rejection;
- [ ] real generation from the TypeScript `Codepotg.yml` fixture;
- [ ] real generation from the Dart `Codepotg.yaml` fixture.

## Verification commands

From `packages/python/codepotg`:

```bash
python -m pytest tests/codepot_file/test_loader.py -q
python -m pytest tests/integration/test_project_template_packs.py -q
python -m pytest -q
python -m ruff check .
```

Manual fixture generation:

```bash
codepotg generate --config tests/fixtures/projects/typescript/Codepotg.yml
codepotg generate --config tests/fixtures/projects/dart/Codepotg.yaml
```

The expected output roots are:

```text
tests/fixtures/projects/typescript/.generated/
tests/fixtures/projects/dart/.generated/
```

## Reporting format

Every completed batch must report:

```text
commit SHA or SHAs
main task items completed
variables made available
fixture templates added or updated
tests added
commands to run
expected generated files
known unexecuted checks or environment limitations
```

## Current batch

### Batch V0 — Project fixture foundation

- [x] define mandatory verifiability rules;
- [x] support `Codepotg.yaml` and `Codepotg.yml` discovery;
- [x] add focused loader tests for both extensions and ambiguity;
- [-] add TypeScript project fixture and shared template pack;
- [-] add Dart project fixture and shared template pack;
- [-] add real generation integration tests;
- [ ] run focused tests and mark the batch complete.
