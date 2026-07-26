# Configuration and pack contract tasks

## CFG-001 — Location-aware document model

**Status:** planned

**Dependencies:** CORE-004

- [ ] Define immutable mapping, sequence, scalar, and null syntax nodes.
- [ ] Preserve source identity, line/column spans, document path, and original key text.
- [ ] Implement safe YAML and JSON parsers behind a document-loader port.
- [ ] Reject duplicate keys and unsafe/unregistered YAML tags.
- [ ] Add in-memory and file-backed parsing tests.

**Acceptance:** structural errors point to exact source locations and no raw loader object enters typed decoders.

## CFG-002 — Schema registry and typed decoder protocol

**Status:** planned

**Dependencies:** CFG-001, CORE-003

- [ ] Register project, pack, and lock document families independently.
- [ ] Resolve each family by `apiVersion`; do not require a redundant root `kind` field.
- [ ] Implement typed decoder, structural validator, semantic validator, serializer, and introspection protocols.
- [ ] Detect duplicate schema registrations and unsupported versions.
- [ ] Prove no old `tasks` or `paths.yaml` fallback exists.

**Acceptance:** `codepotg.yaml`, `CodepotgPack.yaml`, and `codepotg.lock.yaml` decode only through their documented v2 families.

## CFG-003 — Simplified project root model

**Status:** planned

**Dependencies:** CFG-002

- [ ] Implement root `apiVersion`, `name`, named semantic `sources`, `executables`, `security`, `commands`, and ordered `packs`.
- [ ] Implement source-adapter ID plus adapter-owned file/location/options.
- [ ] Keep raw YAML out of template contexts.
- [ ] Reject unknown fields with source-spanned suggestions.
- [ ] Reject project-level `language`, `tasks`, `templateDir`, `registries`, and `use`.

**Tests:** minimal/local/Git/mixed project examples, invalid IDs, unsafe paths, and duplicate keys.

## CFG-004 — Executable and security model

**Status:** planned

**Dependencies:** CFG-003

- [ ] Implement project executable names/paths.
- [ ] Implement pack executable defaults and per-instance/project replacement precedence.
- [ ] Implement pack-command approval policy while keeping host policy authoritative.
- [ ] Validate unknown executable references before execution.
- [ ] Expose executable and permission metadata for configure/editor tooling.

**Acceptance:** packs can recommend tools without choosing an executable the project cannot replace or granting themselves permission.

## CFG-005 — Exact project and pack commands

**Status:** planned

**Dependencies:** CFG-004

- [ ] Decode keyed `before` and `after` command mappings.
- [ ] Implement `executable`, opaque `arguments`, `cwd`, timeout, optional state, and typed environment/capability requests.
- [ ] Preserve exact argument boundaries; never derive install arguments from dependency maps.
- [ ] Reject implicit shell strings unless an explicit permitted shell mode is added later.
- [ ] Preserve command source spans and stable command IDs from mapping keys.

**Acceptance:** CodepotG schedules and executes exact arguments without understanding pnpm/npm/Flutter/Dart install syntax.

## CFG-006 — Direct pack source and instance model

**Status:** planned

**Dependencies:** CFG-003

- [ ] Implement `source.local` as a path relative to `codepotg.yaml`.
- [ ] Implement `source.git`, required `ref`, and optional repository-relative `path`.
- [ ] Reject mixed local/Git forms and missing Git refs.
- [ ] Implement project-local instance name, `input`, scalar `output`, options, bindings, executable overrides, and project-owned commands.
- [ ] Keep pack identity/version in the resolved manifest rather than duplicating it in project config.
- [ ] Validate duplicate instances, missing inputs, and unsafe output paths.

**Acceptance:** the same pack can be configured twice, and every instance is self-contained without registry alias drift.

## PACKCFG-001 — Compact pack identity and compatibility

**Status:** planned

**Dependencies:** CFG-002, CORE-003

- [ ] Implement root `apiVersion`, `id`, `version`, `description`, optional direct metadata, and `requires`.
- [ ] Remove required `kind`, `metadata`, and `integration` nesting.
- [ ] Infer whether a pack emits files, consumes inputs, requires bindings, or has commands from actual declarations.
- [ ] Add schema introspection and human examples.

**Acceptance:** pack identity is readable at the root and no boolean trait matrix duplicates manifest facts.

## PACKCFG-002 — Filesystem discovery and ignore contract

**Status:** planned

**Dependencies:** PACKCFG-001

- [ ] Use `templates/` as the default content root.
- [ ] Apply pack-root `.gitignore` plus manifest `include` and `exclude` rules deterministically.
- [ ] Treat `_partials/**` as non-emitting template-engine content.
- [ ] Discover literal templates, static files, and binaries without explicit registration.
- [ ] Render templates at their literal relative path and strip only the recognized engine suffix.
- [ ] Copy static/binary files unchanged.
- [ ] Treat literal `.gitignore` as a control file; allow `.gitignore.jinja` to emit `.gitignore`.
- [ ] Ensure docs/tasks/caches outside `templates/` are not emitted.

**Acceptance:** ordinary files need no `files`, `filePatterns`, `role`, or static registry entries.

## PACKCFG-003 — Options, bindings, executables, and commands

**Status:** planned

**Dependencies:** PACKCFG-001, CFG-004, CFG-005

- [ ] Implement compact typed option declarations including `choices` and inferred simple types.
- [ ] Implement public binding catalog with required state, description, docs, and adapter-owned validation.
- [ ] Implement pack executable defaults.
- [ ] Implement exact pack before/after commands keyed by ID.
- [ ] Ensure projects may replace executable names/paths and may disable/override commands through typed configuration.
- [ ] Keep package-manager/dependency conversion out of core.

**Acceptance:** an independent pack can set itself up through approved exact commands without a dependency-install DSL.

## PACKCFG-004 — Selection emission registry

**Status:** planned

**Dependencies:** PACKCFG-002, PATH-001..PATH-005, PLAN selection/import contracts

- [ ] Implement one root `selections` mapping as the only explicit emission registry.
- [ ] Implement `paths` as a compact list relative to the pack-instance output root.
- [ ] Implement versioned fixed selectors with `.each` and `.all` cardinality.
- [ ] Infer default contexts from fixed selectors and support optional inline aliases.
- [ ] Implement `{selectionKey}` folders and built-in `{root}`.
- [ ] Implement explicit `imports: localName: selectionKey` dependency declarations.
- [ ] Implement ordered `exports: [selectionKey]` including barrels exporting barrels.
- [ ] Implement explicit per-emission `symbols` and selection-level external `bindings` usage.
- [ ] Reject arbitrary `from`/`as` selectors, unknown keys, cycles, conflicts, and invented semantic filenames.

**Acceptance:** the canonical TypeORM, TypeScript SDK, and Flutter SDK pack examples decode without root `paths`, `files`, `filePatterns`, roles, or profiles.

## RULE-001 — Typed patch protocol

**Status:** planned

**Dependencies:** CFG-002

- [ ] Implement explicit typed patch protocols only for fields intentionally project-overridable.
- [ ] Distinguish absent, set, remove, and reset states.
- [ ] Prohibit generic recursive dictionary merge.
- [ ] Add property tests for deterministic merges.

## BIND-001 — Binding values and validation

**Status:** planned

**Dependencies:** PACKCFG-003, language port

- [ ] Implement module, barrel, project path, package, namespace, text, value, and artifact binding models.
- [ ] Validate project values against pack binding declarations and target adapter capability.
- [ ] Track exact selection/template consumers.
- [ ] Never treat generated selection imports as external bindings.

## BIND-002 — Generated import registry and conflicts

**Status:** planned

**Dependencies:** PACKCFG-004, PLAN dependency graph, language import port

- [ ] Require every cross-selection generated dependency under `imports`.
- [ ] Match semantic dependencies to declared selection symbols.
- [ ] Compute least-required symbols for `.each`, `.all`, global, and parent-scoped emissions.
- [ ] Support direct emission groups and barrel selections as import providers.
- [ ] Reject missing providers, duplicate local names, ambiguous scopes, and conflicting symbols.
- [ ] Produce an immutable language-neutral import plan for adapters/templates.

**Acceptance:** no template can silently consume a generated symbol from an undeclared selection.

## Acceptance gate

This group is complete when:

- all example project/pack YAML files decode into immutable models;
- local/Git source forms are mutually exclusive and Git refs are required;
- literal files and static files need no manifest registry;
- fixed selectors and selection folders are introspectable;
- imports/exports/symbols form a validated acyclic graph;
- exact command arguments survive decode/serialize unchanged;
- unknown fields and unsafe paths produce source-spanned diagnostics;
- no old `tasks`/`paths.yaml` decoder or semantic filename convenience exists.
