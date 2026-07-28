# Dryv orchestrator implementation plan

## Goal

Deliver one production-grade path from typed project configuration and neutral semantic input to a complete validated artifact plan, rendered memory output, deterministic archive, and managed transactional filesystem output.

This plan does not restore the old Dryv runtime or make commands, Git, cache, or incremental generation implicit.

## Branch

```text
chatgpt/codepotx-restart-orchestrator
```

## Status vocabulary

```text
planned       no implementation accepted
in_progress   implementation is actively changing
implemented   code and focused tests are present; full verification is open
review        implementation is synchronized and all required commands passed
blocked       exact external/public contract is missing
complete      merged to base with recorded verification and clean audit
```

No task moves directly from `implemented` to `complete`.

---

## ORCH-001 — Core foundation verification

**Status:** review required

- verify the reorganized `dryv` package against the synchronized checkout;
- run all unit/contract/architecture/distribution tests;
- verify public facades and wheel contents;
- preserve no-old-runtime and no-flat-module boundaries.

**Acceptance:** core wheel installs and imports before any adapter wheel is installed.

## ORCH-002 — Authoring-aligned kernel additions

**Status:** implemented

Implemented typed neutral contracts for:

- `TagSet`;
- `GuidanceNote` and `GuidanceKind`;
- `FieldCapabilities`, lifecycle, query, and field references;
- `ValueSource`;
- `Presentation` and `PresentationEntry`.

Implemented indexing, validation, public exports, and fixed selectors.

**Verification still required:** focused property tests, complete core suite, JSON/YAML round trips, selector ordering, and compatibility review with `dryv-author`.

## ORCH-003 — Canonical IR transport

**Status:** implemented

- strict `Contract` → document/JSON/YAML;
- exact document/JSON/YAML → `Contract`;
- explicit type/enum/name/reference discriminators;
- deterministic compact JSON;
- safe YAML;
- duplicate-key, cycle, depth, item, version, type, field, and finite-number validation;
- core validation before encoding and after decoding.

**Acceptance:** exact round trip for every connected IR fixture and stable compact hash across processes.

## ORCH-004 — Built-in IR source adapter

**Status:** implemented

- `ir` plugin and `codepot-ir` alias;
- memory/file JSON/YAML;
- 32 MiB source limit;
- no adapter options;
- canonical digest;
- cancellation and structured diagnostics;
- Python entry-point registration.

**Acceptance:** independent installed-wheel discovery and source conformance pass.

## ORCH-005 — Strict project configuration

**Status:** implemented

- safe YAML/JSON;
- duplicate-key rejection;
- exact `dryv.dev/v1` family;
- typed sources and ordered pack instances;
- local/Git locator discrimination;
- immutable options, bindings, executables, security, and command documents;
- unknown-field rejection;
- path safety;
- recursive/depth/item/non-finite value rejection.

**Open refinement:** add source spans to typed configuration diagnostics.

## ORCH-006 — Strict pack manifest

**Status:** implemented

- metadata and compatibility;
- include/exclude;
- typed option declarations and defaults;
- binding declarations;
- fixed selections;
- imports, exports, paths, symbols, and binding usage;
- executables/commands preserved for the separate command lane;
- unknown-field rejection.

**Open refinement:** add richer option type descriptors and schema introspection for configure/IDE use.

## ORCH-007 — Plugin discovery and isolated sessions

**Status:** implemented

- discover source, target, and engine entry points;
- load zero-argument factories;
- enforce public protocols;
- validate plugin conflicts;
- longest engine suffix;
- longest target suffix;
- missing/ambiguous plugin diagnostics;
- no process-global instance registry.

**Acceptance:** real installed core/OpenAPI/Jinja/TypeScript/Dart wheels coexist and resolve exactly once.

## ORCH-008 — Local pack authorization and discovery

**Status:** implemented

- local pack contained beneath project root;
- mandatory `templates/`;
- deterministic traversal;
- GitWildMatch include/exclude;
- pack-root `.gitignore`;
- symlink containment;
- template, partial, static, and binary classification;
- control ignore files excluded;
- selection-folder validation;
- partials registered and never emitted;
- engine and target inference.

**Acceptance:** adversarial symlink, ignore, duplicate, static, binary, and suffix fixtures pass on Windows and POSIX.

## ORCH-009 — Pack compatibility and dependency graph

**Status:** implemented

- `requires.dryv` and `requires.ir` specifiers;
- unknown compatibility keys rejected;
- unsatisfied versions rejected;
- unknown imported/exported selections rejected;
- selection dependency cycles rejected before planning;
- command declarations fail readiness until the command runtime exists.

## ORCH-010 — Fixed selector execution

**Status:** implemented current registry

Implemented:

```text
groups.all
groups.each
groups.schemas.each
groups.schemas.objects.each
groups.schemas.enums.each
groups.operations.each
groups.views.each
groups.storage.mappings.each
groups.workflows.each
groups.policies.each
groups.events.each
groups.value_sources.each
presentations.each
presentations.entries.each
```

Zero selected contexts emit zero artifacts.

**Planned only after proven pack needs:** `.all` collection variants beyond groups, child selectors, operation input/output/failure selectors, workflow steps, view parts, and explicit global indexes.

## ORCH-011 — Safe path expressions

**Status:** implemented

- `(expression)`;
- `((literal))`;
- known root/property traversal;
- semantic naming projections;
- scalar-only results;
- no calls, private attributes, arbitrary graph traversal, runtime roots, or nested syntax;
- POSIX-relative output validation.

**Acceptance:** deterministic property and malformed-expression matrix passes.

## ORCH-012 — Artifact identity and first-pass planning

**Status:** implemented

- stable invocation/artifact identity separate from destination;
- semantic/group/selection/template cause tracking;
- selection paths and template path composition;
- engine suffix stripping with target suffix retained;
- symbols evaluated before rendering;
- target output validation;
- path and identity collision diagnostics;
- no renderer/writer call on invalid plan.

## ORCH-013 — Generated dependency resolution

**Status:** implemented first behavior version

- two-pass planning;
- imports and exports resolved after all providers exist;
- exact semantic-ID match;
- group-scope fallback;
- declared selection fallback;
- target consistency;
- target-adapter module/path facts;
- explicit declared symbols;
- deterministic module ordering.

**Open hardening:** ambiguous several-provider diagnostics and richer planner-owned scope/provider descriptors required by official complex packs.

## ORCH-014 — Prepared render context

**Status:** implemented first behavior version

Always active:

```text
project
pack
options
bindings
artifact
target
imports
exports
contract
```

Selector roots include group/schema/operation/view/mapping/workflow/policy/event/value_source/presentation/entry.

Relationships are resolved before rendering. Tags and guidance are available through safe aliases.

**Acceptance:** context schema snapshot, strict-undefined, immutability, cycle, item/depth, and no-runtime-object tests pass.

## ORCH-015 — Jinja tag queries

**Status:** implemented

Safe only on verified `TagSet` records:

```text
has
has_any
has_all
under
empty
```

Other record callables remain denied.

**Acceptance:** adversarial callable/alias tests and the full Jinja security suite pass.

## ORCH-016 — Rendering runtime

**Status:** implemented

- one isolated generation session;
- source normalization;
- semantic validation;
- planning;
- dry run;
- UTF-8 template source;
- declared partials;
- engine rendering;
- cancellation;
- diagnostics aggregation;
- static/binary passthrough;
- deterministic sorted `MemoryOutput`.

## ORCH-017 — Memory writer

**Status:** implemented

Memory output is the primary generated result used by tests, archives, previews, and filesystem writers.

## ORCH-018 — Deterministic archive writer

**Status:** implemented

- ZIP;
- sorted entries;
- fixed timestamps and permissions;
- fixed compression;
- exact generated bytes;
- atomic archive-file replacement.

## ORCH-019 — Managed transactional filesystem writer

**Status:** implemented

- generation-state manifest;
- exact content hashes;
- create/change/leave/delete/protect reporting;
- unmanaged collision refusal;
- manual-edit protection;
- safe stale deletion;
- staged replacements;
- rollback;
- state outside dependency lock.

**Open hardening:** interruption/fault-injection matrix across every commit step and Windows file-lock behavior.

## ORCH-020 — Plan inspection and explanation

**Status:** implemented first behavior version

- deterministic plan document/JSON;
- artifact ID/path lookup;
- template, selection, semantic, group, target, symbol, import/export facts;
- cause summary.

**Planned:** full semantic-to-artifact impact graph and plan reload.

## ORCH-021 — Python API

**Status:** implemented

```python
generate(..., dry_run=True)
generate(...)
generate_to_files(...)
```

All return structured results. No CLI-only execution path exists.

## ORCH-022 — Thin CLI

**Status:** implemented

```text
dryv plan
dryv generate --memory
dryv generate [--destination]
```

CLI prints structured JSON and uses the Python services.

## ORCH-023 — Command planning, approvals, and execution

**Status:** planned separate trust lane

Current behavior is fail-closed with `CMD_APPROVAL_REQUIRED`.

Required implementation:

- typed exact command records;
- executable resolution and replacement precedence;
- project/pack/instance provenance;
- before/after and staged/post-commit phases;
- stable command digest;
- project/host policy;
- downloaded-pack approval default;
- environment allowlist;
- working-directory containment;
- timeout and process-tree cleanup;
- cancellation;
- action reporting;
- no shell interpolation;
- no package-manager inference.

## ORCH-024 — Git pack provider and dependency lock

**Status:** planned separate distribution lane

Current behavior is fail-closed with `PACK_PROVIDER_UNSUPPORTED`.

Required implementation:

- generic Git, not GitHub-only;
- existing Git credentials only;
- requested ref and immutable resolved commit;
- contained subdirectory snapshot;
- safe cache;
- `dryv.lock.yaml`;
- no credentials in config/lock/state/diagnostics;
- command approval tied to exact locked pack identity;
- offline reuse and integrity verification.

## ORCH-025 — Cross-operation content cache

**Status:** planned after full verification

- complete behavior key;
- source/IR/config/pack/template/partial/adapter/options/bindings/path facts;
- bounded materialization;
- corruption recovery;
- no generated state in dependency lock.

## ORCH-026 — Explain and impact graph

**Status:** partial

Artifact explanation exists. Still required:

- semantic-to-selection edges;
- selection-to-artifact edges;
- generated provider edges;
- template/include edges;
- command/action edges;
- changed semantic/pack/config blast radius;
- serializable IDE/MCP contract.

## ORCH-027 — Conservative incremental generation

**Status:** blocked on ORCH-026 and deterministic full-generation proof

Incremental output must equal a fresh complete generation byte-for-byte.

## ORCH-028 — Configure and project update API

**Status:** planned

- schema introspection;
- configure/check/add-pack;
- safe in-place YAML edits preserving unrelated content where possible;
- readiness actions;
- no hidden profiles or registry/use model.

## ORCH-029 — Official pack vertical fixtures

**Status:** blocked on adapter repair verification and official packs

Required connected fixture:

```text
schemas + enums
operations + failures + HTTP facets
storage mappings
views + parts + triggers
value sources
policies + events
workflows
presentations
namespaced tags + guidance
```

Generate at least TypeScript and Dart from the same contract, compile/analyze outputs, and assert exact paths/imports/exports.

## ORCH-030 — Release verification and merge

**Status:** in_progress

Required commands:

```bash
cd packages/python/dryv
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -vv
rm -rf build dist
python -m build
```

Then:

1. build real core/OpenAPI/Jinja/TypeScript/Dart wheels;
2. install together in a new environment;
3. discover all entry points;
4. run canonical IR JSON/YAML generation;
5. run OpenAPI generation;
6. generate official TypeScript/Dart fixtures to memory, ZIP, and managed filesystem;
7. compile/analyze generated projects;
8. run cancellation, collision, symlink, rollback, ownership, security, and determinism tests;
9. inspect wheel/sdist contents;
10. verify no `.github` files and no old runtime imports;
11. merge only after the branch is synchronized and clean.

## Completion gate

The orchestrator is complete only when ORCH-001..ORCH-022 and ORCH-030 pass. ORCH-023..ORCH-029 remain independently versioned follow-on capabilities unless the release explicitly claims them.

The runtime must never claim support for Git, commands, cache, impact, or incremental generation while their tasks remain open.
