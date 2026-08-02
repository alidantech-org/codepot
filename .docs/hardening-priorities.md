# Codepot hardening priorities

## Purpose

This document identifies the areas most likely to determine whether Codepot becomes a dependable platform or an over-engineered generator. The priorities are architectural and behavioral. They apply regardless of implementation language.

## Priority model

- **P0 — existential:** failure invalidates determinism, safety, or semantic authority.
- **P1 — adoption critical:** the architecture may work, but users or pack authors cannot trust or use it effectively.
- **P2 — scale critical:** needed before broad ecosystems, large contracts, or enterprise use.

## P0 — one semantic authority

### Risk

Authoring frontends, adapters, tags, pack manifests, or template helpers may quietly introduce meaning that is absent from the canonical Runtime IR.

### Required hardening

- Every behavior-affecting concept has one typed kernel definition.
- Authoring compilation ends at the public immutable contract.
- Source adapters cannot create private semantic nodes.
- Packs cannot define new semantic kinds, facets, selectors, or context roots.
- Tags remain bounded hints and never replace required relationships.
- `extensions` and `raw` preserve unknown data without granting it semantic authority.
- Kernel additions follow a versioned design-change procedure.
- Cross-frontend conformance fixtures prove equivalent canonical output.

### Failure signal

A pack must inspect source-specific raw metadata to implement normal behavior.

## P0 — canonical identity, ordering, hashing, and transport

### Risk

The same contract may serialize differently, acquire unstable IDs, or appear to delete and recreate items during ordinary refactoring.

### Required hardening

- Stable semantic identities are distinct from display names and paths.
- Canonical ordering is defined for every collection.
- Canonical JSON/YAML serialization has one normalized meaning.
- Digests exclude nondeterministic timestamps, environment paths, object addresses, and iteration order.
- Rename and move operations preserve identity when intended.
- Transport round trips preserve semantics and provenance.
- Large-contract representations such as indexed JSONL remain infrastructure formats, not alternate semantics.
- IR and behavior versions are independently explicit where necessary.

### Failure signal

Two machines produce different contract digests from the same authored input.

## P0 — compatibility semantics

### Risk

Codepot can propagate a change consistently while consistently breaking every consumer.

### Required hardening

- Each kernel object and relationship defines compatible, conditionally compatible, and breaking changes.
- Compatibility checks compare against an explicit prior contract or lock.
- Policy is separate from detection.
- Diagnostics identify affected semantic consumers and generated artifacts.
- Pack/runtime/plugin compatibility is checked before planning.
- Compatibility rules are versioned and testable.
- Unknown extension semantics receive no fabricated guarantees.
- Renames, removals, constraint tightening, nullability, defaults, enum changes, operation changes, policy changes, event changes, and storage changes receive explicit rules.

### Failure signal

A breaking semantic change reaches rendering without a classified compatibility result.

## P0 — complete planning before side effects

### Risk

Rendering or writing starts before collisions, dependencies, commands, approvals, and destinations are known.

### Required hardening

A valid plan registers:

- source and pack identities;
- semantic selections and invocations;
- artifact identities and normalized destinations;
- symbols, imports, exports, and provider matches;
- bindings, options, and effective values;
- static files and partial dependencies;
- commands and approval requirements;
- ownership actions and stale-file decisions;
- collisions, cycles, ambiguity, and path-policy checks;
- impact and explanation edges.

Renderers and writers reject incomplete or foreign plans.

### Failure signal

A renderer discovers a destination or dependency that was absent from the plan.

## P0 — managed output safety

### Risk

Generation overwrites user work, deletes unrelated files, or leaves partial output after failure.

### Required hardening

- Unmanaged collisions fail by default.
- Managed files record content digests and ownership identities.
- Modified managed files are protected unless a deliberate policy resolves them.
- Only unchanged stale managed files are removed automatically.
- Writes occur through staging and atomic commit where supported.
- Failed commits restore the previous valid state.
- State updates occur only after artifact commit succeeds.
- Concurrent generation is locked by project/output scope.
- Path traversal, symlink escape, case folding, reserved filenames, and cross-platform normalization are tested.
- Dry run and execution share the same plan.

### Failure signal

A failed generation changes the visible project or corrupts ownership state.

## P0 — dependency and symbol correctness

### Risk

Generated files depend on hidden filename conventions or renderer-time lookups, causing missing imports, cycles, or ambiguous providers.

### Required hardening

- Selections declare symbols and generated dependencies explicitly.
- Provider matching uses semantic identity, scope, symbol, pack instance, and destination facts.
- Ambiguity is an error rather than an arbitrary choice.
- Cycles are detected before rendering.
- Module/path facts are calculated by bounded target adapters.
- Templates own syntax but cannot select undeclared providers.
- Barrels and aggregates are ordinary planned artifacts.
- Cross-pack dependencies are visible in the project plan and lock.

### Failure signal

A template searches the filesystem or rendered text to guess an import provider.

## P0 — deterministic plugin isolation

### Risk

Plugins mutate global state, redefine semantics, perform hidden I/O, or make results depend on discovery order.

### Required hardening

- Runtime instances own immutable plugin graphs.
- Discovery returns validated factories, not imported global registrations.
- Plugin IDs, versions, capabilities, and behavior versions are explicit.
- Capability conflicts and duplicate IDs fail deterministically.
- Plugins receive least-authority contexts.
- Source, target, engine, provider, cache, writer, and command capabilities remain separate.
- Optional plugin removal removes only its capability.
- Plugin order is either semantically irrelevant or explicitly configured and recorded.
- Conformance suites are public and reusable by third parties.

### Failure signal

Importing a plugin package changes another runtime instance.

## P0 — supply-chain and command security

### Risk

Remote packs and plugins can execute arbitrary code or alter projects without transparent approval.

### Required hardening

- Pack source resolution produces immutable commits and content digests.
- Credentials never enter project configuration, locks, diagnostics, or generated state.
- Downloaded pack commands require explicit approval by default.
- Commands are exact argument vectors, never hidden shell fragments.
- Command working directories, environment permissions, timeouts, outputs, and cancellation are controlled.
- Templates run in a sandbox with resource limits appropriate to the engine.
- Static files and paths are validated before staging.
- Trust decisions are scoped to exact source identity and digest.
- Marketplace discovery cannot bypass runtime locking and trust.
- Pack signatures or attestations can be added later without replacing content-addressed verification.

### Failure signal

Changing a remote branch changes generation without a lock update or visible approval.

## P1 — explanation and bidirectional traceability

### Risk

The system is deterministic but opaque, forcing users to debug runtime internals.

### Required hardening

For every artifact, Codepot explains:

- source semantic identities;
- selector and match reason;
- active group and parent contexts;
- pack, template, and static-file origins;
- path-expression evaluation;
- option and binding sources;
- provider/import/export decisions;
- ownership and lifecycle action;
- compatibility and impact status.

For every semantic item, Codepot lists affected packs, invocations, artifacts, and commands.

Explanations are stable runtime artifacts with machine and human presentations.

### Failure signal

A user must add debug prints to discover why a template was selected.

## P1 — generated and handwritten composition

### Risk

Users either edit generated files and fear regeneration or cannot express custom logic cleanly.

### Required hardening

- Packs declare ownership strategy per artifact.
- Preferred extension patterns are composition, interfaces, adapters, hooks, partial classes where target-appropriate, and handwritten neighboring modules.
- Generated regions are supported only where robust parsing and ownership can be proven.
- Manual-edit conflicts produce actionable recovery options.
- Pack documentation identifies safe extension points and migration paths.
- A project can stop using a pack without losing semantic source or handwritten work.
- Custom code dependencies on generated symbols are testable and compatibility-aware.

### Failure signal

Routine business logic requires editing a fully managed generated file.

## P1 — semantic scope discipline

### Risk

The kernel expands into framework vocabulary or a universal programming model.

### Required hardening

A new concept enters the kernel only when it:

1. has stable meaning across several targets;
2. affects validation, compatibility, selection, impact, or traceability;
3. cannot be represented as an existing object or relationship;
4. has at least two realistic pack/source simulations;
5. has clear attachment, identity, ordering, and migration rules;
6. is useful beyond one project or framework;
7. does not encode executable target algorithms.

### Failure signal

A kernel proposal is justified primarily by one framework’s class or folder structure.

## P1 — pack author usability

### Risk

The architecture is precise but authoring a pack is harder than maintaining custom scripts.

### Required hardening

- Filesystem conventions infer safe facts; manifests contain only non-inferable behavior.
- Selector and context catalogs are searchable and versioned.
- Pack validation identifies exact source locations and fixes.
- A pack playground can inspect contexts and planned outputs without writing.
- Fixtures simulate realistic contracts, not only toy schemas.
- Pack conformance tests cover determinism, portability, dependencies, paths, and ownership.
- Pack templates remain readable without complex helper layers.
- Pack upgrades expose compatibility and migration information.

### Failure signal

A simple pack requires a large manifest that duplicates its directory structure.

## P1 — project usability and feedback

### Risk

Users cannot tell what will happen or why a configuration is invalid.

### Required hardening

The standard workflow should be understandable as:

```text
inspect → validate → plan → review → generate → verify → trace
```

- Human output is concise and progressive.
- Machine output is stable, complete, and styling-free.
- Diagnostics use stable codes, severity, source spans, semantic IDs, and remediation guidance.
- Plans summarize additions, updates, removals, skips, conflicts, and commands.
- Non-interactive behavior never prompts.
- Interactive confirmation never changes the plan.
- Configuration has schemas and editor support.
- Defaults are safe and visible.

### Failure signal

Users routinely run generation just to learn what the plan would have been.

## P1 — documentation truth and product identity

### Risk

Contributors follow superseded CodepotG or CodepotX rules because active and archived documents conflict.

### Required hardening

- One root status page names the active architecture and package maturity.
- Normative documents are labeled and ordered.
- Archived documents begin with replacement links and superseded vocabulary warnings.
- Verification status is dated and tied to a commit.
- Product naming distinguishes Codepot ecosystem, Dryv runtime, authoring frontends, packs, CLI, and future language.
- Public docs do not claim stable releases that progress evidence has not verified.

### Failure signal

Two active READMEs describe different packages as the long-term runtime authority.

## P1 — end-to-end evidence

### Risk

Unit tests prove components but not the actual developer workflow.

### Required hardening

- At least two independent real projects use the same packs.
- Reference changes are repeated over time.
- Generated targets compile, analyze, migrate, and run.
- Cross-machine output digests match.
- failure injection proves rollback;
- agent and human workflows use the same public runtime API;
- baseline comparisons measure conventional tools and direct agent editing;
- manual-edit and pack-upgrade scenarios are tested.

### Failure signal

The principal demonstration always starts from an empty project and never performs a breaking evolution.

## P2 — performance and large-contract behavior

### Required hardening

- Memory, CPU, file count, and plan size have published reference limits.
- Full generation remains the correctness baseline.
- Caching keys include every behavior-affecting input.
- Incremental generation is conservative and falls back to broader work when impact is uncertain.
- Lazy/indexed source representations preserve canonical semantics.
- Parallelism never changes ordering, diagnostics, or output.
- Cancellation leaves no visible partial state.

## P2 — pack ecosystem quality

### Required hardening

- Pack maturity and maintenance status are explicit.
- Compatibility ranges are machine-checkable.
- Conformance results and fixture coverage are published.
- Security/trust metadata is visible.
- Pack composition and conflicts are validated.
- Deprecated packs provide migration guidance.
- Marketplace ranking does not imply trust; runtime locks remain authoritative.

## P2 — governance and sustainability

### Required hardening

- Architecture decision records explain changes.
- Kernel and behavior versions have support windows.
- Deprecation is time-bounded.
- Contributor responsibilities are separated by subsystem.
- Generated compatibility fixtures are retained permanently.
- Release evidence is reproducible from the exact commit.
- Project metrics include maintenance cost and adoption, not only feature count.

## Recommended hardening sequence

```text
1. Canonical identity and transport
2. Kernel and authoring conformance
3. Complete planner and compatibility analysis
4. Dependency/symbol graph
5. Managed transactional writer
6. Explanation and trace graph
7. Reference packs and generated-project validation
8. Agent-safe runtime operations
9. Distribution, locks, trust, and pack certification
10. Performance, incremental work, and marketplace features
```

## Release principle

No package family should be labeled production-ready because its architecture is approved or its unit tests pass independently. Release readiness requires evidence that the exact packaged artifacts can be installed together, discover each other through public contracts, plan and generate a real connected project, protect user files, reproduce output, and validate the generated targets.
