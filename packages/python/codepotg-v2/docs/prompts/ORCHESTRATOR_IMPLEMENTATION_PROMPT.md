# Verify, repair, complete, and audit the CodepotG v2 orchestrator

You are completing and independently auditing the first production CodepotG v2 orchestration runtime.

This is implementation work. Read the code, run the commands, repair failures, add missing focused tests, update evidence, and merge only after every claimed gate passes.

Do not redesign Codepot around the old generator, OpenAPI, a generic graph, runtime frameworks, database engines, or target-language renderers.

---

# Repository and branch

```text
Repository:
alidantech-org/codepot

Base branch:
chatgpt/codepotx-restart

Feature branch:
chatgpt/codepotx-restart-orchestrator

Core package:
packages/python/codepotg-v2
```

Use the existing feature branch. Do not create a different branch.

The branch name contains one slash only.

Never create, modify, restore, or depend on:

```text
.github/
.github/workflows/
.github/actions/
```

Never force-push.

Do not rebase a published feature branch. Synchronize by merging the latest base.

---

# Mandatory reading order

## Governance

```text
packages/python/codepotg-v2/docs/00-governance/00-approved-architecture.md
packages/python/codepotg-v2/docs/00-governance/01-agent-working-rules.md
packages/python/codepotg-v2/docs/00-governance/03-glossary-and-ownership.md
packages/python/codepotg-v2/docs/00-governance/04-closed-semantic-kernel.md
```

## Authoring-aligned IR

```text
packages/python/codepotg-v2/docs/01-foundation/05-authoring-aligned-ir.md
packages/python/codepotg-v2/docs/01-foundation/06-canonical-ir-transport.md
packages/python/codepotg-author/docs/IDEA.md
packages/python/codepotg-author/docs/design/01-architecture-and-boundaries.md
packages/python/codepotg-author/docs/design/02-ref-engine.md
packages/python/codepotg-author/docs/design/03-authoring-model.md
packages/python/codepotg-author/docs/design/05-transport.md
```

## Project, pack, and generation

```text
packages/python/codepotg-v2/docs/02-configuration/01-project-config-specification.md
packages/python/codepotg-v2/docs/02-configuration/02-pack-manifest-specification.md
packages/python/codepotg-v2/docs/03-generation/01-template-file-model.md
packages/python/codepotg-v2/docs/03-generation/02-selection-folder-patterns-and-static-files.md
packages/python/codepotg-v2/docs/03-generation/03-planning-execution-and-transaction.md
packages/python/codepotg-v2/docs/03-generation/04-orchestrator-runtime.md
packages/python/codepotg-v2/docs/03-generation/05-template-context-contract.md
```

## Tasks and evidence

```text
packages/python/codepotg-v2/docs/tasks/00-master-plan.md
packages/python/codepotg-v2/docs/tasks/ORCHESTRATOR_PLAN.md
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md
packages/python/codepotg-v2/docs/tasks/PROGRESS.md
```

## Adapter boundaries

```text
packages/python/codepotg-v2/src/codepotg/ports/source.py
packages/python/codepotg-v2/src/codepotg/ports/templates.py
packages/python/codepotg-v2/src/codepotg/ports/target.py
packages/python/codepotg-v2/docs/04-plugins/01-plugin-system.md
packages/python/codepotg-v2/docs/04-plugins/02-language-adapter-contract.md
packages/python/codepotg-v2/docs/04-plugins/03-template-engine-adapter-contract.md
```

---

# Non-negotiable architecture

## One IR

There is one closed neutral `codepotg.ir.Contract`.

Do not add:

- a second author graph;
- generic node/edge/fact bags;
- entity/model/resource/frontend/UI roots;
- arbitrary semantic plugin registration;
- source-specific objects in render contexts.

## Authoring direction

Python/Pydantic authoring may be concise and expressive, but compiles only to the public closed IR.

Author refs, builders, Pydantic models, Python functions, decorators, modules, and registries never enter IR, transport, planning, or templates.

## Emitted syntax

Templates, macros, partials, and static files own every emitted character.

Target adapters only:

- declare target descriptors;
- validate identifiers and output paths;
- calculate module/path facts.

They never render source.

## Tags

Tags are immutable namespaced Boolean hints. They do not replace typed semantics or refs.

Supported Jinja calls exist only on verified tag records:

```text
has
has_any
has_all
under
empty
```

Do not widen callable or attribute access for ordinary context records.

## Presentations

Presentations describe neutral application surfaces and view placements. They are not React, Flutter, desktop, CLI-framework, or layout trees.

## Commands, Git, cache, and incremental work

The current orchestrator is fail-closed for unimplemented trust/distribution lanes:

```text
CMD_APPROVAL_REQUIRED
PACK_PROVIDER_UNSUPPORTED
```

Do not silently ignore declarations.

Do not implement a rushed unsafe shell executor or unaudited Git downloader while fixing the local orchestrator. Those tasks remain ORCH-023 and ORCH-024 unless the user explicitly expands this work.

---

# Primary implementation areas to audit

```text
packages/python/codepotg-v2/src/codepotg/config/**
packages/python/codepotg-v2/src/codepotg/domain/ir/**
packages/python/codepotg-v2/src/codepotg/domain/generation/**
packages/python/codepotg-v2/src/codepotg/generation/**
packages/python/codepotg-v2/src/codepotg/runtime/**
packages/python/codepotg-v2/src/codepotg/application/**
packages/python/codepotg-v2/src/codepotg/infrastructure/**
packages/python/codepotg-v2/src/codepotg/cli/**
packages/python/codepotg-v2/src/codepotg/ir/codec.py
packages/python/codepotg-template-jinja/src/codepotg_template_jinja/context/**
packages/python/codepotg-template-jinja/src/codepotg_template_jinja/sandbox/**
```

Tests:

```text
packages/python/codepotg-v2/tests/**
packages/python/codepotg-template-jinja/tests/integration/test_tag_queries.py
```

---

# Required implementation audit

## 1. Imports and package architecture

Prove:

- all public imports work from a clean install;
- no import cycle exists among root API, generation, runtime, infrastructure, IR codec, and plugin discovery;
- no old `packages/python/codepotg` implementation is imported;
- public facades expose only intentional APIs;
- tests mirror production boundaries;
- no flat module/package collision exists.

## 2. Configuration

Test:

- YAML and JSON;
- duplicate keys;
- unknown fields;
- exact API version;
- non-string keys;
- recursive YAML aliases;
- maximum depth/items;
- non-finite numbers;
- local/Git locator exclusivity;
- source and output path safety;
- pack options/defaults/choices/required values;
- binding declarations and usage;
- commands fail readiness rather than being ignored.

## 3. IR additions

Audit:

- `TagSet` grammar and methods;
- guidance categories and uniqueness;
- field lifecycle/query/reference capabilities;
- value-source relationships;
- presentation/view relationships;
- semantic identity collisions;
- selector ordering;
- public exports;
- no target/runtime detail in these contracts.

## 4. Canonical transport

Test every connected IR type through:

```python
contract_from_json(contract_to_json(contract)) == contract
contract_from_yaml(contract_to_yaml(contract)) == contract
```

Test:

- deterministic compact JSON across processes;
- duplicate keys;
- wrong envelope/version;
- unknown type, enum, and field;
- malformed refs/names;
- recursive YAML aliases;
- depth/item limits;
- invalid cross-references after decoding;
- source-adapter file and memory paths;
- installed entry-point discovery;
- canonical digest equality.

Do not serialize Python module paths or object addresses.

## 5. Plugin runtime

Test installed factories for:

```text
ir/openapi source adapters
jinja engine
typescript target
dart target
```

Prove:

- duplicate IDs and aliases fail;
- missing and ambiguous suffixes fail;
- factory exceptions are redacted safely;
- instances are session-owned;
- separate sessions do not leak mutable state.

## 6. Pack discovery

Test:

- local pack containment;
- project-root containment;
- symlink escape;
- required `templates/`;
- GitWildMatch include/exclude;
- pack-root `.gitignore`;
- `.gitignore` control files are not emitted;
- nested/unknown selection folders;
- `_partials` handling;
- template/static/binary classification;
- longest engine and target suffixes;
- declaration suffixes such as `.d.ts.jinja`;
- target-neutral rendered documents;
- deterministic traversal.

## 7. Compatibility and graph validation

Test:

- current CodepotG and IR ranges;
- invalid and unsatisfied ranges;
- unknown requirement keys;
- unknown import/export selection references;
- self and multi-node dependency cycles;
- no rendering when validation fails.

## 8. Selection and expressions

Test every published selector, including empty contracts/groups.

Prove:

- zero contexts emit zero artifacts;
- literal files emit once;
- selections remain root-first;
- no unregistered selector is accepted;
- path expressions allow only documented scalar paths;
- literal parentheses work;
- private/callable/runtime traversal fails;
- output paths remain POSIX-relative and contained.

## 9. Artifact planning

Test:

- stable artifact identity;
- output collisions;
- duplicate IDs;
- engine suffix removal and target suffix preservation;
- target validation;
- static/binary exact bytes;
- selection paths;
- symbols;
- deterministic plan order;
- no renderer or writer called for an invalid plan.

## 10. Generated dependencies

Test:

- semantic-ID provider matching;
- group fallback;
- selection fallback;
- missing and ambiguous providers;
- target mismatch;
- relative/package/alias module facts using real TypeScript/Dart adapters;
- symbols and stable order;
- imports/exports are facts only, never emitted statements.

Do not hide ambiguous provider behavior. Add an error where several provider artifacts cannot be selected deterministically.

## 11. Render contexts

Snapshot and document the prepared context for every selector.

Prove:

- all documented roots exist only in valid scopes;
- inactive roots are strict undefined;
- options/bindings/imports/exports are attribute-readable immutable records;
- operation, storage, view, event, value-source, and presentation refs are resolved;
- tags work through direct safe aliases;
- guidance remains explanatory;
- no runtime/filesystem/secret/callable object enters context;
- context source values remain unchanged after success and failure.

## 12. Rendering

Use the real Jinja engine.

Test:

- strict undefined;
- partial include/import/inheritance;
- cancellation;
- render-byte limits;
- template syntax diagnostics;
- tag methods;
- target-neutral text files;
- TypeScript and Dart files;
- static/binary passthrough;
- deterministic repeated output.

Run the complete Jinja security suite after any sandbox edit.

## 13. Writers

### Memory

Prove sorted deterministic output and exact content.

### ZIP

Prove equal output creates identical archive bytes, fixed timestamps/permissions, exact entries, and atomic file replacement.

### Managed filesystem

Test:

- first create;
- exact leave;
- safe managed change;
- unmanaged collision refusal;
- manual edit refusal;
- unchanged stale deletion;
- changed stale protection;
- malformed state file;
- path traversal;
- symlink destination escape;
- injected failures at every commit phase;
- rollback of writes, deletes, and state;
- Windows file-lock behavior where available.

## 14. Python API and CLI

Prove:

```text
generate(dry_run=True)
generate()
generate_to_files()
codepotg plan
codepotg generate --memory
codepotg generate
```

return equivalent structured status, diagnostics, plans, and outputs.

CLI must not contain generation logic.

## 15. Plan inspection

Test deterministic plan JSON and artifact explanation by ID/path. Include causes, dependencies, target, symbols, selection, and template.

---

# Required connected fixtures

## Neutral contract

Include:

```text
Company
User with company reference
UserCreate/UserRead
ListCompanies
CreateUser/ListUsers
CompanyChoices value source
User storage mapping
Users view with parts/triggers
UserCreated event
ProvisionUser workflow
Admin presentation
namespaced tags
guidance
```

## TypeScript pack

Generate at least:

```text
models
operation/client files
barrel/index
presentation route registry or neutral manifest
documentation/static file
```

Compile with a local TypeScript compiler when available.

## Dart pack

Generate at least:

```text
models
operation/client files
barrel/index
presentation route registry or neutral manifest
documentation/static file
```

Run `dart analyze` when available.

The same IR must drive both packs.

---

# Required commands

## Core

```bash
cd packages/python/codepotg-v2
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -vv
rm -rf build dist
python -m build
```

## Jinja

```bash
cd packages/python/codepotg-template-jinja
python -m pip install -e ../codepotg-v2
python -m pip install -e ".[dev]"
python -m ruff check src tests benchmarks
python -m ruff format --check src tests benchmarks
python -m pytest -vv
rm -rf build dist
python -m build
```

## Other adapters

Run their full package commands and audit-fix ledgers:

```text
packages/python/codepotg-openapi/docs/tasks/AUDIT_FIXES.md
packages/python/codepotg-language-typescript/docs/tasks/AUDIT_FIXES.md
packages/python/codepotg-language-dart/docs/tasks/AUDIT_FIXES.md
```

## Installed-wheel environment

Build and install real wheels for:

```text
codepotg-core
codepotg-openapi
codepotg-template-jinja
codepotg-language-typescript
codepotg-language-dart
```

Then:

- discover all entry points;
- load canonical IR JSON/YAML;
- load OpenAPI;
- plan and generate TypeScript and Dart fixtures;
- write memory, ZIP, and managed filesystem output;
- compile/analyze generated projects;
- verify a clean environment contains no editable-source imports.

---

# Commit sequence

Use coherent commits with tests beside changes. Suggested remaining sequence:

```text
fix(orchestrator): repair import and typing failures
fix(orchestrator): harden configuration and transport bounds
fix(orchestrator): harden pack discovery and planning
fix(orchestrator): resolve dependency ambiguity
fix(orchestrator): stabilize prepared contexts and tag sandbox
fix(orchestrator): harden managed writer rollback
feat(orchestrator): add connected real-adapter fixtures
test(orchestrator): complete installed-wheel matrix
docs(orchestrator): record verified behavior and blockers
```

Do not squash all fixes into one opaque commit.

---

# Synchronization

Before work:

```bash
git fetch origin
git switch chatgpt/codepotx-restart-orchestrator
git merge --no-edit origin/chatgpt/codepotx-restart
```

After every one or two coherent commits:

```bash
git fetch origin
git log --oneline HEAD..origin/chatgpt/codepotx-restart
```

Merge base updates normally. Do not rebase or force-push.

Preserve all claims and progress rows when resolving:

```text
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md
packages/python/codepotg-v2/docs/tasks/PROGRESS.md
```

---

# Documentation updates

Update only after verification:

```text
packages/python/codepotg-v2/README.md
packages/python/codepotg-v2/docs/README.md
packages/python/codepotg-v2/docs/03-generation/README.md
packages/python/codepotg-v2/docs/tasks/00-master-plan.md
packages/python/codepotg-v2/docs/tasks/ORCHESTRATOR_PLAN.md
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md
packages/python/codepotg-v2/docs/tasks/PROGRESS.md
packages/python/codepotg-author/docs/IDEA.md
packages/python/codepotg-author/docs/tasks/00-package-plan.md
packages/python/codepotg-author/docs/tasks/PROGRESS.md
```

Remove or clearly supersede examples that claim selectors or context roots not present in the public registry.

Do not mark Git, commands, cache, impact, configure, or incremental tasks complete unless their implementation and tests are part of this branch.

---

# Merge gate

Do not merge into `chatgpt/codepotx-restart` when any of these remain:

- core, Jinja, adapter, or connected fixture test failure;
- Ruff or formatting failure;
- build failure;
- installed-wheel discovery failure;
- import cycle;
- ambiguous provider behavior;
- unbounded YAML/IR graph;
- symlink/path escape;
- partial filesystem commit;
- false documentation claim;
- dirty working tree;
- branch behind base;
- `.github` change;
- old Codepot runtime import.

After all claimed gates pass:

```bash
git switch chatgpt/codepotx-restart
git pull --ff-only origin chatgpt/codepotx-restart
git merge --no-ff chatgpt/codepotx-restart-orchestrator \
  -m "merge: integrate CodepotG v2 generation orchestrator"
git push origin chatgpt/codepotx-restart
```

Leave the feature branch available for audit.

---

# Final report

Report exact evidence:

```text
starting base SHA
final feature SHA
base merge SHA
commit list
changed paths
core test counts
Jinja test counts
adapter test counts
Ruff results
format results
build results
wheel contents
entry-point discovery
IR JSON/YAML round trips
OpenAPI normalization result
TypeScript generation and compiler result
Dart generation and analyzer result
memory output result
ZIP determinism result
managed writer and rollback result
symlink/path security result
cancellation result
plan/explain result
remaining blocked tasks
confirmation of no .github files
confirmation of no old runtime imports
confirmation that templates own emitted syntax
clean working tree
```

Do not claim success from earlier agent logs. Reproduce the commands against the final synchronized branch.
