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

- [x] global variables and project metadata;
- [ ] file and emission context;
- [x] naming variants used by template content and output paths;
- [x] resource variables and collections;
- [x] schema groups and schema identity;
- [-] fields and currently available primitive facts;
- [-] currently available defaults and explicit-null source preservation; normalized constants and examples remain pending;
- [ ] arrays, objects, composition, and references;
- [-] operation identity plus parameter, request-body, and response counts;
- [ ] root and operation security;
- [ ] cache read and invalidation rules;
- [ ] access definitions and resolved uses;
- [ ] runtime transport and hooks;
- [ ] sources and query metadata;
- [ ] entities, inherited fields, backend fields, relations, and constraints;
- [ ] frontend definitions, components, screens, and uses;
- [-] immutable root raw source and root extensions are implemented and tested; object-level raw data, diagnostics, and loss reports remain pending;
- [ ] imports and dependency planning;
- [ ] safe empty and failure behavior.

## Config compatibility gate

Both standard CodepotG filenames are supported:

```text
Codepotg.yaml
Codepotg.yml
```

Required tests:

- [x] explicit `.yaml` loading test passed;
- [x] explicit `.yml` loading test passed;
- [x] automatic `.yaml` discovery test passed;
- [x] automatic `.yml` discovery test passed;
- [x] ambiguity failure test passed for projects containing both names;
- [x] legacy `CodepotFile.yml` and `CodepotFile.yaml` rejection test passed;
- [x] real TypeScript generation test passed for `Codepotg.yml`;
- [x] real Dart generation test passed for `Codepotg.yaml`;
- [x] manual TypeScript CLI generation emitted all nine expected files;
- [x] manual Dart CLI generation emitted all nine expected files.

## Verification commands

From `packages/python/codepotg`:

```bash
python -m pytest tests/codepot_file/test_loader.py -q
python -m pytest tests/contracts/test_lossless_source.py -q
python -m pytest tests/integration/test_project_template_packs.py -q
python -m pytest tests/cli/test_generate_command.py tests/cli/test_config_filename_output.py -q
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

Each project currently emits nine files:

```text
contract/project.<language extension>
contract/collections.<language extension>
contract/source.<language extension>
schemas/user_status.<language extension>
schemas/user_model.<language extension>
schemas/create_user_body.<language extension>
operations/list_users.<language extension>
operations/create_user.<language extension>
resources/users.<language extension>
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

## Current batches

### Batch V0 — Project fixture foundation

- [x] define mandatory verifiability rules;
- [x] support `Codepotg.yaml` and `Codepotg.yml` discovery;
- [x] add focused loader tests for both extensions and ambiguity;
- [x] add TypeScript project fixture and shared template pack;
- [x] add Dart project fixture and shared template pack;
- [x] add real generation integration tests and exact emitted-content assertions;
- [x] statically verify path selection, template scanning, and adapter variable compatibility;
- [x] execute loader tests: 14 passed;
- [x] execute project-pack integration tests: 5 passed;
- [x] manually generate the TypeScript fixture: 9 files created;
- [x] manually generate the Dart fixture: 9 files created.

### Batch V1 — Lossless root OpenAPI source

- [x] retain a deep copy of the complete OpenAPI root in the inference graph;
- [x] preserve existing inference serialization output by default;
- [x] allow explicit raw inference serialization with `include_raw=True`;
- [x] add recursively immutable `FrozenMap` source values;
- [x] expose `api.raw` without changing existing `api.meta` behavior;
- [x] expose all root `x-*` values as `api.extensions`;
- [x] add direct tests for immutability, deep-copy isolation, extensions, ordered arrays, and explicit null;
- [x] add TypeScript and Dart source templates using collision-safe bracket access;
- [x] assert source values through real generated project files;
- [x] locally render-check both source templates with strict Jinja undefined handling;
- [x] execute lossless source tests: 4 passed.

### Batch V2 — Full-suite CLI compatibility repair

- [x] update stale missing-config assertion for `.yaml` and `.yml` support;
- [x] remove the accidental direct `click.testing` dependency;
- [x] keep Typer's public `CliRunner` and isolate filesystem scenarios with Python 3.11 `contextlib.chdir`;
- [x] report the actual resolved config filename in progress output;
- [x] add a regression test proving explicit `Codepotg.yml` output;
- [x] normalize the Ruff-flagged loader-test import block;
- [-] rerun focused CLI tests, the complete suite, and Ruff after pulling the latest branch head.
