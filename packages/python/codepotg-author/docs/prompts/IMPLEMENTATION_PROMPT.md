# AI implementation prompt: build `codepotg-author`

Implement the typed Python authoring compiler for CodepotG v2.

## Repository and branches

```text
Repository: alidantech-org/codepot
Base branch: chatgpt/codepotx-restart
Feature branch: chatgpt/codepotx-restart-codepotg-author
Package: packages/python/codepotg-author
Core: packages/python/codepotg-v2
```

Use exactly one slash in the feature branch. Do not create any additional branch.

```bash
git fetch origin
git switch chatgpt/codepotx-restart
git pull --ff-only origin chatgpt/codepotx-restart
git switch -c chatgpt/codepotx-restart-codepotg-author
```

When the feature branch already exists, track/resume it rather than creating another branch.

Never create, modify, restore, or depend on `.github/**`. Never force-push.

## Goal

Build a concise, strongly typed Python authoring frontend that compiles declarations into the existing public immutable `codepotg.ir.Contract` and supports canonical JSON/YAML round-trip transport.

The authoring layer may be expressive. The compiled IR must remain closed, neutral, deterministic, readable, portable, selector-safe, and oblivious to framework/runtime implementation details.

## Mandatory reading

Read in order:

```text
packages/python/codepotg-v2/docs/00-governance/00-approved-architecture.md
packages/python/codepotg-v2/docs/00-governance/04-closed-semantic-kernel.md
packages/python/codepotg-v2/docs/00-governance/01-agent-working-rules.md
packages/python/codepotg-v2/docs/00-governance/03-glossary-and-ownership.md
packages/python/codepotg-v2/docs/01-foundation/01-package-architecture.md
packages/python/codepotg-v2/docs/03-generation/README.md
packages/python/codepotg-v2/docs/04-plugins/README.md
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md

packages/python/codepotg-author/README.md
packages/python/codepotg-author/docs/README.md
packages/python/codepotg-author/docs/IDEA.md
packages/python/codepotg-author/docs/design/*.md
packages/python/codepotg-author/docs/tasks/00-master-plan.md
packages/python/codepotg-author/docs/tasks/01-dependencies-and-parallelism.md
packages/python/codepotg-author/docs/tasks/PARALLEL_WORK.md
packages/python/codepotg-author/docs/tasks/PROGRESS.md
```

The approved v2 architecture and `codepotg-author` design override CodepotG 1.0.0 and archived rewrite patterns.

## Claim the work

Update both:

```text
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md
packages/python/codepotg-author/docs/tasks/PARALLEL_WORK.md
```

Claim initially:

```text
AUTHOR-001..AUTHOR-013
AUTHOR-015..AUTHOR-020
AUTHOR-022
AUTHOR-024
AUTHOR-027..AUTHOR-030
```

Do not claim blocked kernel-evolution tasks as implemented:

```text
AUTHOR-014
AUTHOR-021
AUTHOR-023
AUTHOR-025
AUTHOR-026
extended portions of AUTHOR-019 and AUTHOR-028
```

Record exact public-core blockers. Continue every independent task.

## Allowed edit scope

Primary implementation:

```text
packages/python/codepotg-author/**
```

Coordination only:

```text
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md
```

Do not modify:

```text
packages/python/codepotg-v2/src/codepotg/**
packages/python/codepotg-openapi/**
packages/python/codepotg-template-jinja/**
packages/python/codepotg-language-typescript/**
packages/python/codepotg-language-dart/**
packages/python/codepotg/src/**
.github/**
```

A separate approved core task is required for new semantic models, facets, selectors, template contexts, validation, and IR versions.

## Architecture invariants

1. There is one semantic IR.
2. Authoring declarations are compiler input, not a second graph.
3. Pydantic is an authoring dependency; core does not depend on it.
4. Every ref belongs to an explicit `Author` session.
5. No process-global decorator, model, schema, ref, cache, or compiler registry.
6. Authoring builders, Pydantic classes, Python functions, and arbitrary objects never enter IR or template contexts.
7. Schemas remain structural; do not restore entity/model/request/response schema kinds.
8. Query/command/listener/scheduled are authoring sugar for ordinary operations.
9. Only public core facets may compile.
10. The package does not register selectors or template variables.
11. Tags, guidance, field capabilities, value sources, presentations, and missing HTTP facts fail with exact blockers until core publishes them.
12. No target/framework/database-specific authoring or typed pack binding layer.
13. No rendering, template selection, output planning, writing, CLI, command, or OpenAPI ownership.
14. JSON/YAML contains compiled IR, never authoring state.

## Required package structure

Use the prepared subsystem directories. Replace `.gitkeep` files only as matching implementations/tests are added. Keep source and tests mirrored. Do not create flat giant modules.

Expected major source boundaries:

```text
src/codepotg_author/
├── author.py
├── options.py
├── result.py
├── diagnostics/
├── declarations/
├── refs/
├── pydantic/
├── schemas/
├── storage/
├── operations/
├── policies/
├── events/
├── views/
├── presentations/
├── workflows/
├── tags/
├── guidance/
├── compilation/
│   └── passes/
├── transport/
└── validation/
```

## Public API and typing

Use Python 3.11+ features, generics, protocols, overloads, `Annotated`, `Self`, frozen/slots dataclasses, Pydantic v2, strict Pyright, and strict mypy fixtures.

Implement distinct immutable refs such as schema, field, operation, event, policy, storage, view, workflow, and workflow-step refs. Do not collapse public refs into `Ref[Any]`.

Use typed field selector lambdas with a restricted runtime proxy. Prove unknown fields and wrong ref kinds fail statically and at runtime.

## Compiler

Implement explicit passes in the order documented in `design/07-compiler-and-validation.md`. Each declaration and ref compiles/resolves exactly once per session. Unsupported concepts produce diagnostics and do not partially enter the contract.

Final flow:

```text
collect
→ freeze
→ validate author declarations
→ assign deterministic IDs
→ link typed refs
→ compile public-core semantics
→ construct immutable Contract
→ codepotg.ir.validate_contract
→ canonicalize/digest
→ optional JSON/YAML
```

Expected invalid authoring returns structured diagnostics. Do not leak ordinary Pydantic/linker/parser exceptions.

## JSON/YAML is required

Implement a strict versioned canonical Codepot IR document, not an author-specific snapshot.

Required:

```python
result.to_document()
result.to_json()
result.to_yaml()
contract_to_document(...)
contract_to_json(...)
contract_to_yaml(...)
contract_from_document(...)
contract_from_json(...)
contract_from_yaml(...)
```

Prove:

```python
contract_from_json(contract_to_json(contract)) == contract
contract_from_yaml(contract_to_yaml(contract)) == contract
```

Requirements:

- duplicate-key-safe YAML;
- no unsafe YAML object construction;
- strict versions and unknown fields;
- deterministic ordering;
- canonical semantic IDs and refs;
- JSON/YAML semantic parity;
- core validation after decode;
- canonical JSON digest;
- no Pydantic/builders/callables/classes/memory addresses;
- readable pretty output suitable for shipping and direct semantic input.

When canonical codec ownership requires a public core contract, implement the package-local canonical codec only through public IR APIs and record the ownership blocker. Do not modify core privately.

## Tags and future concepts

Design package APIs may be stubbed and tested to return `AUTHOR_CORE_UNSUPPORTED`, but do not claim compilation for missing core semantics.

Tags are immutable namespaced Boolean hints, not refs or key/value configuration. Presentations are neutral application topology, not framework UI. Value sources are operation-backed candidate data, not HTTP/frontend fetching. Guidance is descriptive and never creates semantics.

## Old and archived code

Study as read-only pattern evidence:

```text
packages/nodejs/codepot-openapi/**
archives/deprecated/src/contract/types/**
archives/deprecated/src/compiler/**
packages/python/codepotg/**
```

Keep useful ideas:

- concise typed builders;
- definitions returning refs;
- immutable usage methods;
- compiler prepasses and resolver maps;
- multi-pass compilation;
- portable compiled refs;
- debug documents.

Do not copy:

- OpenAPI as semantic authority;
- resources/routes/entities/models/DTOs as kernel roots;
- `unknown`/arbitrary metadata escape bags;
- process-global registries;
- target/framework rendering;
- old runtime internals;
- compatibility decoders;
- authoring objects in compiled output.

The new package must not import CodepotG 1.0.0 or Node code.

## Tests

Mirror source boundaries and include:

- unit tests for every declaration/ref/compiler/transport subsystem;
- static typing positive and negative fixtures;
- architecture tests for boundaries and import side effects;
- contract tests for immutable public output and deterministic diagnostics;
- Pydantic recursive/nested/union/enum/Annotated fixtures;
- projection and derivation exact assertions;
- wrong-kind, missing, duplicate, foreign-session, forward-ref, and cycle tests;
- current-core storage/policy/event/operation/facet/view/workflow tests;
- exact blocker tests for unsupported core concepts;
- canonical JSON/YAML round trips and malformed documents;
- one realistic cross-group fixture;
- deterministic repeated/concurrent session tests;
- performance and memory smoke tests;
- wheel/sdist and isolated installation tests.

Architecture tests must prove no OpenAPI, Jinja, target adapter, pack, writer, CLI, command, framework, database runtime, old generator, private core, `.github`, or sibling package ownership.

## Verification

From `packages/python/codepotg-v2`:

```bash
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -vv
python -m build
```

From `packages/python/codepotg-author` in a clean environment:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ../codepotg-v2
python -m pip install -e ".[dev]"

python -m ruff check src tests benchmarks examples
python -m ruff format --check src tests benchmarks examples
python -m pyright
python -m mypy src tests/typing

python -m pytest tests/unit -vv
python -m pytest tests/contracts -vv
python -m pytest tests/architecture -vv
python -m pytest tests/typing -vv
python -m pytest tests/integration -vv
python -m pytest tests/transport -vv
python -m pytest tests/performance -vv
python -m pytest tests/distribution -vv
python -m pytest -vv

rm -rf build dist
python -m build
```

Install the real core and author wheels into a separate environment and repeat imports, connected compilation, JSON/YAML round trips, and wheel-content checks. `git status --short` must be empty.

## Commit sequence

Use coherent commits with tests beside code:

```text
feat(codepotg-author): add author session and typed refs
feat(codepotg-author): add property and schema authoring
feat(codepotg-author): add Pydantic model compiler and projections
feat(codepotg-author): add storage policy event and operation authoring
feat(codepotg-author): add view workflow and compiler passes
test(codepotg-author): add typing architecture and connected coverage
feat(codepotg-author): add canonical IR JSON YAML transport
test(codepotg-author): add distribution performance and round-trip gates
docs(codepotg-author): record support blockers and verification evidence
```

## Keep synchronized

After every one or two coherent commits:

```bash
git fetch origin
git log --oneline HEAD..origin/chatgpt/codepotx-restart
```

When base advanced:

```bash
git merge --no-edit origin/chatgpt/codepotx-restart
```

Do not rebase a published feature branch. Do not force-push. Preserve all other task claims during conflict resolution.

Before final verification:

```bash
git fetch origin
git switch chatgpt/codepotx-restart-codepotg-author
git merge --no-edit origin/chatgpt/codepotx-restart
```

Rerun every required command, push the feature branch, confirm the base has not advanced, then merge:

```bash
git push -u origin chatgpt/codepotx-restart-codepotg-author

git switch chatgpt/codepotx-restart
git pull --ff-only origin chatgpt/codepotx-restart
git merge --no-ff chatgpt/codepotx-restart-codepotg-author \
  -m "merge: integrate CodepotG v2 Python authoring compiler"
git push origin chatgpt/codepotx-restart
```

Do not merge with any failing lint, format, typing, tests, build, wheel, transport, blocker, scope, synchronization, or clean-tree gate.

## Final report

Report exact:

- starting base SHA, feature SHA, merge SHA, commit list, changed files;
- public API and package structure;
- dependencies and reasons;
- supported authoring concepts;
- blocked core concepts and exact contracts;
- ref kinds and usage methods;
- Pydantic support and explicit unsupported behavior;
- compiler pass list and deterministic ID policy;
- JSON/YAML envelope/version, round-trip, digest, and direct-input results;
- all test counts and command outputs;
- Ruff, format, Pyright, mypy, build, wheel, isolated install results;
- realistic fixture and performance results;
- confirmation of no private core/old runtime/framework/target/rendering/writer/CLI/command/.github behavior;
- confirmation the feature branch remains available and working tree is clean.

After the report, stop for independent audit.
