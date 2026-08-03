# Configuration and pack contract tasks

Configuration decodes typed project/pack documents only. It cannot extend the semantic kernel, selector registry, expression roots, or template-context contract.

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

**Acceptance:** `dryv.yaml`, `DryvPack.yaml`, and `dryv.lock.yaml` decode only through documented v2 families.

## CFG-003 — Simplified project root model

**Status:** planned

**Dependencies:** CFG-002

- [ ] Implement root `apiVersion`, `name`, named semantic `sources`, `executables`, `security`, `commands`, and ordered `packs`.
- [ ] Implement source-adapter ID plus adapter-owned file/location/options.
- [ ] Keep raw YAML out of template contexts.
- [ ] Reject unknown fields with source-spanned suggestions.
- [ ] Reject project-level `language`, `tasks`, `templateDir`, `registries`, `use`, facet modules, semantic extensions, and selector declarations.

**Tests:** minimal/local/Git/mixed project examples, invalid IDs, unsafe paths, and duplicate keys.

## CFG-004 — Executable and security model

**Status:** planned

**Dependencies:** CFG-003

- [ ] Implement project executable names/paths.
- [ ] Implement pack executable defaults and per-instance/project replacement precedence.
- [ ] Implement pack-command approval policy while keeping host policy authoritative.
- [ ] Validate unknown executable references before execution.
- [ ] Expose executable and permission metadata for configure/editor tooling.

**Acceptance:** packs can recommend tools without granting themselves permission or hiding executable behavior.

## CFG-005 — Exact project and pack commands

**Status:** planned

**Dependencies:** CFG-004

- [ ] Decode keyed `before` and `after` command mappings.
- [ ] Implement `executable`, opaque `arguments`, `cwd`, timeout, optional state, and typed environment/capability requests.
- [ ] Preserve exact argument boundaries; never derive install arguments from dependency maps.
- [ ] Reject implicit shell strings unless an explicit permitted shell mode is added later.
- [ ] Preserve command source spans and stable command IDs from mapping keys.

**Acceptance:** Dryv schedules exact arguments without understanding npm/pnpm/Flutter/Dart syntax in semantic core.

## CFG-006 — Direct pack source and instance model

**Status:** planned

**Dependencies:** CFG-003

- [ ] Implement `source.local` as a path relative to `dryv.yaml`.
- [ ] Implement `source.git`, required `ref`, and optional repository-relative `path`.
- [ ] Reject mixed local/Git forms and missing Git refs.
- [ ] Implement project-local instance name, `input`, scalar `output`, options, bindings, executable overrides, and project-owned commands.
- [ ] Keep pack identity/version in the resolved manifest rather than duplicating it in project config.
- [ ] Validate duplicate instances, missing inputs, and unsafe output paths.

**Acceptance:** the same pack can be configured twice and every instance is self-contained without registry alias drift.

## PACKCFG-001 — Compact pack identity and compatibility

**Status:** planned

**Dependencies:** CFG-002, CORE-003

- [ ] Implement root `apiVersion`, `id`, `version`, `description`, optional direct metadata, and `requires`.
- [ ] Remove required `kind`, `metadata`, and `integration` nesting.
- [ ] Infer capabilities from actual selections, bindings, templates, and commands rather than a boolean trait matrix.
- [ ] Include IR, naming, selection, and target-path compatibility requirements.
- [ ] Add schema introspection and human examples.

**Acceptance:** pack identity is readable at the root and no manifest field claims semantic-kernel ownership.

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
- [ ] Implement public binding catalog with required state, description, docs, and typed validation.
- [ ] Implement pack executable defaults.
- [ ] Implement exact pack before/after commands keyed by ID.
- [ ] Ensure projects may replace executable names/paths and may disable/override commands through typed configuration.
- [ ] Keep package-manager/dependency conversion out of semantic core.
- [ ] Reject options or bindings that attempt to add semantic objects, facets, selectors, expression properties, or arbitrary context values.

**Acceptance:** a pack can configure authored templates and approved commands without redefining Dryv semantics.

## PACKCFG-004 — Root-first selection emission registry

**Status:** planned

**Dependencies:** PACKCFG-002, PATH-001..PATH-005, PLAN selection/dependency contracts

- [ ] Implement one root `selections` mapping as the only explicit emission registry.
- [ ] Implement `paths` as a compact list relative to the pack-instance output root.
- [ ] Implement versioned fixed selectors beginning with `groups` or an active parent such as `group`.
- [ ] Implement `.each` and `.all` cardinality.
- [ ] Infer default contexts and support optional inline aliases without shadowing.
- [ ] Implement `{selectionKey}` folders and built-in `{root}`.
- [ ] Implement explicit `imports: localName: selectionKey` dependency declarations.
- [ ] Implement ordered `exports: [selectionKey]` including barrels exporting barrels.
- [ ] Implement explicit per-emission `symbols` and selection-level external `bindings` usage.
- [ ] Document global selectors as exceptional/discouraged project-wide views.
- [ ] Reject `resource`, `model`, `entity`, frontend/UI, reversed-root, arbitrary `where/traverse/depth`, `from/as`, unknown keys, cycles, conflicts, and invented semantic filenames.

**Acceptance:** storage, TypeScript SDK, Dart SDK, Flutter/view, workflow, access, and event examples decode using only known root-first selectors.

## PACKCFG-005 — Closed-kernel and syntax-ownership enforcement

**Status:** planned

**Dependencies:** PACKCFG-001..PACKCFG-004, IR-005, target/engine ports

- [ ] Reject `facetModules`, semantic node/edge/fact declarations, selector queries, expression-root registration, and template-context extension fields.
- [ ] Reject language rule sections that ask adapters to render types, literals, imports, exports, comments, validators, decorators, or framework syntax.
- [ ] Permit only documented target detection/path-validation options.
- [ ] Add precise diagnostics pointing pack authors to template macros/partials for output syntax.
- [ ] Add architecture fixtures proving packs cannot expand the kernel.

## RULE-001 — Typed patch protocol

**Status:** planned

**Dependencies:** CFG-002

- [ ] Implement explicit typed patch protocols only for fields intentionally project-overridable.
- [ ] Distinguish absent, set, remove, and reset states.
- [ ] Prohibit generic recursive dictionary merge.
- [ ] Add property tests for deterministic merges.

## BIND-001 — External binding values and validation

**Status:** planned

**Dependencies:** PACKCFG-003, target path-validation port

- [ ] Implement module, project path, package, namespace, text, value, and artifact binding models.
- [ ] Validate project values against pack declarations and target path/identifier capabilities.
- [ ] Track exact selection/template consumers.
- [ ] Never treat generated selection imports as external bindings.
- [ ] Expose facts only; templates author binding/import syntax.

## BIND-002 — Generated dependency registry and conflicts

**Status:** planned

**Dependencies:** PACKCFG-004, PLAN dependency graph, target path-validation port

- [ ] Require every cross-selection generated dependency under `imports`.
- [ ] Match consumer/provider artifacts by semantic identity, active group scope, selection key, and declared symbols.
- [ ] Compute required providers and symbols for `.each`, `.all`, project-wide, and active-parent emissions.
- [ ] Support direct emission groups and authored barrel selections as providers.
- [ ] Resolve destination-relative and target-aware module/path facts.
- [ ] Reject missing providers, duplicate local names, ambiguous scopes, conflicting symbols, and cycles.
- [ ] Produce immutable dependency descriptors for templates.
- [ ] Prohibit pre-rendered import/export statements.

**Acceptance:** no template silently consumes an undeclared generated symbol and no adapter authors the import text.

## Acceptance gate

This group is complete when:

- all example project/pack YAML files decode into immutable models;
- local/Git source forms are mutually exclusive and Git refs are required;
- literal/static/binary files need no manifest registry;
- root-first fixed selectors and active-parent scopes are introspectable;
- packs cannot add semantic objects, facets, selectors, expression roots, or contexts;
- imports/exports/symbols form a validated semantic artifact graph;
- generated dependency descriptors contain facts, not emitted syntax;
- exact command arguments survive decode/serialize unchanged;
- unknown fields and unsafe paths produce source-spanned diagnostics;
- no old `tasks`/`paths.yaml` decoder or semantic filename convenience exists.
