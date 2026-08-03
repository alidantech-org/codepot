# Source-level implementation audit

## Scope

This audit checks whether the active Dryv source code on `chatgpt/develop` supports the architecture described in the research paper. It is a focused source review of the runtime facade, generation session, planner, managed filesystem writer, and Python author compiler. It is not a claim that every implementation file or every package test has been independently executed in this research pass.

The purpose is to separate:

- behavior visible in active source;
- architecture that is partly implemented;
- capabilities still described as planned or incomplete.

## Files inspected

- [`packages/python/dryv/src/dryv/runtime/facade.py`](../packages/python/dryv/src/dryv/runtime/facade.py)
- [`packages/python/dryv/src/dryv/runtime/session.py`](../packages/python/dryv/src/dryv/runtime/session.py)
- [`packages/python/dryv/src/dryv/application/generate.py`](../packages/python/dryv/src/dryv/application/generate.py)
- [`packages/python/dryv/src/dryv/generation/planner.py`](../packages/python/dryv/src/dryv/generation/planner.py)
- [`packages/python/dryv/src/dryv/infrastructure/ownership.py`](../packages/python/dryv/src/dryv/infrastructure/ownership.py)
- [`packages/python/dryv-author/src/dryv_author/compiler.py`](../packages/python/dryv-author/src/dryv_author/compiler.py)

These files were compared with the active architecture and progress documentation.

## Finding 1 — a reusable runtime facade is implemented

`DryvRuntime` is an immutable runtime facade that owns one plugin graph and exposes:

- `snapshot()`;
- `plan()`;
- `generate()`;
- `generate_to_files()`.

The facade delegates to application operations and accepts an injected writer factory. Runtime creation can discover installed plugins or use an explicitly supplied plugin graph.

### Assessment

**Demonstrated in source.** The runtime is not merely an embedded CLI function. The implementation supports the architecture rule that different frontends should consume one reusable in-process runtime.

### Remaining proof

- installed wheel integration across the full package family;
- concurrent/server-hosted lifecycle tests;
- stable versioned machine operation contracts beyond direct language calls.

## Finding 2 — planning and rendering are separate stages

`GenerationSession.generate()` performs:

1. project authorization;
2. source normalization;
3. project planning;
4. early return with `READY` status for dry run;
5. rendering only when dry run is false.

An invalid plan returns failure before rendering. The facade’s `plan()` operation calls the same generation session with dry-run behavior.

### Assessment

**Demonstrated in source.** The plan is not a post-render summary.

### Remaining hardening

The current `GenerationPlan` path should grow to contain all intended behavior-affecting facts, including richer compatibility, impact, command approval, lock, ownership, and explanation information. Separation exists; completeness remains a continuing requirement.

## Finding 3 — source normalization uses bounded adapters

The generation session resolves configured source adapters from the runtime plugin graph and asks them to normalize project-contained input files into public `Contract` values. It collects adapter diagnostics and stops on errors.

### Assessment

**Demonstrated in source.** Source frontends connect to the runtime through a contract-provider boundary.

### Remaining hardening

- direct host-supplied in-memory providers;
- canonical transport providers with complete behavior-version checks;
- remote/large-source behavior where approved;
- conformance across several source frontends.

## Finding 4 — fixed selectors and bounded contexts are implemented

`ProjectPlanner` uses `DEFAULT_SELECTOR_REGISTRY` or an injected selector registry. Pack manifests refer to known selector names. Unknown selectors fail with `PLAN_SELECTOR_UNKNOWN`. Selected items become `SelectionContext` values and are converted into render contexts by `RenderContextBuilder`.

### Assessment

**Demonstrated in source.** Packs do not currently provide an arbitrary general graph query language through this path.

### Remaining hardening

- versioned selector/context catalogs;
- public explanation of match and skip reasons;
- compatibility guarantees for selector changes;
- broader realistic selector fixtures.

## Finding 5 — output collisions and artifact identity collisions are checked before rendering

The planner sorts planned artifacts and reports:

- `PLAN_OUTPUT_COLLISION` when two artifacts resolve to one destination;
- `PLAN_ARTIFACT_ID_COLLISION` when identities collide.

Target adapters validate output paths before the artifact enters the final plan.

### Assessment

**Demonstrated in source.** Core collision checks occur during planning.

### Remaining hardening

- case-insensitive and Unicode-normalized collision behavior;
- richer cross-platform reserved-path checks;
- collision diagnostics with source/template locations;
- policy-controlled project overrides where safe.

## Finding 6 — generated dependencies are explicit but currently bounded

Selections can declare imports and exports referring to other selection keys. The planner resolves provider artifacts and asks the target adapter for module-path facts. Templates receive `ModuleDescriptor` values containing specifier, symbols, provider artifact path, and semantic identity.

Provider matching prefers the same semantic identity, then the same group, then all candidates. Missing providers fail before rendering, and cross-target dependencies are rejected.

### Assessment

**Partly demonstrated.** The important architecture pattern—planned provider descriptors rather than renderer-time source inspection—is real.

### Current limitation

Dependency resolution occurs inside `_plan_pack()` using artifacts from the current pack instance. The current source does not yet implement a complete project-wide cross-pack dependency graph. Provider fallback may also return several candidates rather than classifying every ambiguity as an error.

### Required hardening

- project-wide provider registry;
- exact ambiguity rules;
- cycles across packs;
- explicit dependency cardinality;
- stable provider-selection explanations;
- compatibility of symbol contracts across pack versions.

## Finding 7 — current pack resolution is local-first

The planner and renderer explicitly reject non-local pack sources with `PACK_PROVIDER_UNSUPPORTED`. Project authorization also validates local pack containment within the project root.

### Assessment

**Current source limitation.** Direct Git pack resolution, immutable lock handling, remote trust, and cached pack snapshots are documented architecture goals but are not implemented in this planner/render path.

This validates the research paper’s classification of Git distribution and locking as architecturally supported or planned rather than demonstrated on the reviewed branch.

## Finding 8 — commands are blocked from the normal generation path

The application generation operation rejects project or pack commands with `CMD_APPROVAL_REQUIRED` and states that commands require a separate approved command runtime.

### Assessment

**Demonstrated safety boundary.** The current normal runtime does not silently execute configured commands.

### Remaining hardening

- the separate trusted command plan/runtime;
- exact command identities and arguments;
- approval scope and persistence;
- timeout, cancellation, process-tree handling, environment policy, and audit evidence;
- command inclusion in complete plan and lock behavior.

## Finding 9 — managed output protection is implemented

`ManagedFilesystemWriter` records path and SHA-256 digest in `.dryv/generation-state.json`. It:

- leaves identical files unchanged;
- rejects overwrite of unmanaged files;
- rejects overwrite of manually modified managed files;
- deletes stale managed files only when their content still matches recorded state;
- protects changed stale files;
- stages writes and backups;
- attempts rollback after failure;
- rejects absolute, backslash, dot, and traversal paths;
- verifies resolved destinations remain under the output root.

### Assessment

**Demonstrated in source.** Output ownership is a real implementation capability, not only a design aspiration.

### Remaining hardening

- explicit inter-process or project-scope locking;
- durability guarantees such as flush/fsync policy;
- symlink race analysis during commit;
- platform-specific atomicity and cross-volume behavior;
- structured writer diagnostics instead of generic `ValueError` surfaces;
- richer state including plan, pack, semantic, and artifact identities;
- separate plan of create/change/delete/protect actions before commit;
- crash-recovery fixtures across every operation boundary.

## Finding 10 — the author compiler constructs public Dryv IR

`compile_author()` freezes the author session, expands and orders schema declarations deterministically, compiles public `dryv.ir` values, constructs a `Contract`, and runs `validate_contract()` before returning `AuthoringResult`.

The compiler handles structural schemas and imports core operation, event, policy, storage, view, and workflow types. Frontend declarations are converted into core values rather than passed to templates.

### Assessment

**Demonstrated in source.** The authoring package is operating as a compiler frontend to public IR.

### Current identity limitation

Several IDs are derived from author and declaration names using slugs, including contract and field identities. An ordinary rename can therefore become an identity change unless explicit stable identity support is introduced or used elsewhere. The planned architecture requires identity to be separable from naming.

### Diagnostic limitation

The top-level compiler catches any exception and converts it to one `AUTHOR_COMPILE_FAILED` diagnostic. This protects users from raw exceptions, but it can discard precise source and semantic context for unexpected failures.

### Required hardening

- explicit stable identity authoring and rename tests;
- more granular compiler-pass diagnostics;
- source spans and related locations;
- cycle errors rather than silent temporary-visit behavior where applicable;
- cross-language authoring conformance;
- full canonical transport equivalence.

## Finding 11 — implementation is narrower than approved semantics

The approved authoring design includes rich concepts such as derivation, mappings, capabilities, value sources, presentations, detailed workflows, guidance, and tags. The inspected compiler imports and compiles several major semantic categories, but the source-level spot check does not prove complete implementation of every approved concept or every documented invariant.

### Assessment

**Architecture broader than verified implementation.** This is normal during development but must remain explicit in maturity claims.

## Finding 12 — architecture tests and exact-head verification remain decisive

The progress documentation records strong pre-rebrand evidence and later implementation checkpoints requiring revalidation. Source inspection confirms substantial implementation, but source inspection does not replace:

- unit and property tests;
- package build and isolated installation;
- plugin entry-point discovery;
- generated TypeScript/Dart target validation;
- cross-platform writer tests;
- connected multi-pack project generation;
- real evolution studies.

## Source-level maturity summary

| Capability | Source-level assessment |
|---|---|
| Runtime facade independent of CLI | Implemented |
| Isolated plugin graph | Implemented in facade/composition design |
| Source normalization to core Contract | Implemented |
| Fixed selector planning | Implemented |
| Plan-before-render dry run | Implemented |
| Output and artifact collision checks | Implemented |
| Target module/path facts | Implemented |
| Explicit generated dependency descriptors | Implemented within current pack boundary |
| Project-wide cross-pack dependency graph | Not established by inspected planner |
| Local pack discovery | Implemented |
| Git pack resolution and immutable lock | Not implemented in inspected path |
| Command execution in normal runtime | Intentionally blocked |
| Managed overwrite protection | Implemented |
| Conservative stale cleanup | Implemented |
| Transactional staging/rollback | Implemented baseline; further durability/concurrency hardening needed |
| Authoring compiles to core IR | Implemented |
| Stable identity independent of names | Incomplete in inspected author compiler |
| Complete compatibility/impact/explanation product | Not established by inspected source |
| Full current package-family release verification | Required by progress documentation |

## Immediate implementation priorities confirmed by source

1. Stabilize semantic identity independent of names.
2. Turn current pack-local dependency resolution into a project-wide graph with strict ambiguity and cycle handling.
3. Implement Git pack providers, immutable locks, trust, and cache verification through public ports.
4. Expand plan artifacts to cover compatibility, impact, commands, ownership actions, and explanations.
5. Add structured diagnostics at compiler and writer boundaries.
6. Add inter-process locking and crash/durability tests to managed output.
7. Complete exact-head packaged integration verification.
8. Preserve the current strengths: runtime/CLI separation, fixed selectors, plan-before-render, explicit descriptors, and protected output.

## Conclusion

The active source contains a credible working nucleus of the proposed architecture. Codepot is not merely a paper design. At the same time, the source confirms why the research documents avoid broad completion claims: several differentiating capabilities—especially stable rename identity, project-wide pack composition, Git locking, compatibility, impact, and full trace—remain incomplete or unproven on the reviewed branch.

That is a healthy position if the team uses the existing nucleus as the reference and hardens it in architectural dependency order rather than adding breadth prematurely.
