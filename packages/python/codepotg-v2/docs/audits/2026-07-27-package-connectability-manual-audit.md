# CodepotG v2 package connectability and human-validation audit

Date: 2026-07-27

Branch audited:

```text
chatgpt/codepotx-restart-orchestrator
```

## Executive finding

The ecosystem is not yet fully connected from every intended source.

The strongest currently testable real chain is:

```text
public codepotg.ir authoring
    -> canonical IR JSON/YAML
    -> built-in IR source adapter
    -> orchestrator
    -> local packs
    -> sandboxed Jinja
    -> TypeScript and Dart target adapters
    -> managed generated files
    -> real target compiler/analyzer
```

The following desired chains remain blocked:

```text
codepotg-author -> Contract
OpenAPI -> OpenApiSourceAdapter -> Contract
```

A committed non-pytest workspace exists at:

```text
packages/python/codepotg-v2/examples/manual/connected-project
```

## Supplied verification-log interpretation

The supplied Windows run is valid evidence for the earlier core foundation:

- Ruff passed.
- Ruff formatting passed.
- 30 core tests passed.
- source distribution and wheel built.

It is not evidence for the orchestrator feature branch. The wheel listing contains the original package skeleton but does not contain the new configuration loader, canonical codec, planner, runtime session, CLI implementation, managed writer, or the expanded orchestrator tests. The commands were therefore run from `chatgpt/codepotx-restart`, a stale checkout, or a checkout that did not contain the orchestrator commits.

## Package status

| Package | Implementation status | Connectability status | Human test available now | Release conclusion |
|---|---|---|---|---|
| `codepotg-core` / `codepotg-v2` | Orchestrator implementation is present on the feature branch. | Candidate for local IR-driven generation. | Full connected manual workspace. | Not release-complete until synchronized Ruff, pytest, build, wheel, and human runs pass. |
| built-in canonical IR adapter | Implemented and registered as `ir`. | Connectable to orchestrator. | JSON/YAML bootstrap, plan, render, and write. | Requires installed-wheel discovery verification. |
| `codepotg-template-jinja` | Strong sandboxed implementation with recorded package-level evidence. | Connectable to current render port and tag API. | Real TypeScript and Dart templates in manual workspace. | Review state; rerun complete synchronized suite and wheel test. |
| `codepotg-language-typescript` | Target/path adapter implemented; direct-option audit fix is present. | Connectable to planner module facts. | Generate a complete TypeScript project and run `tsc --noEmit`. | Review state; synchronized build and compiler oracle still required. |
| `codepotg-language-dart` | Target/path adapter implemented; direct-option audit fix is present. | Connectable to planner module facts. | Generate a Dart package and run `dart format` and `dart analyze`. | Review state; real SDK and synchronized wheel test still required. |
| `codepotg-author` | Typed author session, refs, properties, structural schema declarations, and projections exist. | Not connectable to orchestrator because no compiler/final `Contract` result exists. | `audit_authoring_gap.py` records the current declaration boundary. | In progress, not a functioning authoring compiler yet. |
| `codepotg-openapi` | Substantial loading/parsing/resolution/normalization foundation exists. | Not connectable: advertised factory imports missing `codepotg_openapi.adapter`. Installing it can break global plugin discovery. | Negative factory/discovery reproduction only. | Critical blocker; must remain fix-required. |
| legacy `packages/python/codepotg` | Separate v1 generator baseline. | Must not be loaded as a v2 plugin or used to prove v2 behavior. | Historical comparison only. | Out of the v2 release chain. |

## Detailed findings

### 1. Core and orchestrator

Implemented on the feature branch:

- strict project and pack decoding;
- canonical IR JSON/YAML;
- built-in IR source adapter;
- entry-point discovery;
- local pack authorization and GitWildMatch discovery;
- fixed selectors;
- safe path expressions;
- two-pass artifact and generated-dependency planning;
- prepared immutable contexts;
- Jinja render invocation;
- memory output;
- deterministic archive output;
- managed transactional filesystem output;
- CLI plan and generate commands;
- ownership state and collision protection.

Open verification:

- exact synchronized core test count;
- Ruff and format on the feature head;
- PEP 517 build containing all orchestrator modules;
- isolated-wheel CLI and entry-point discovery;
- Windows and POSIX manual writer behavior;
- real TypeScript and Dart generated-project checks.

### 2. `codepotg-author`

The package currently exposes an `Author` declaration registry and typed refs. It can create groups, properties, object/enum schemas, projected schemas, operations, events, policies, storage refs, views, and workflows.

It does not currently expose:

- `Author.compile()`;
- an `AuthoringResult` containing `Contract` and diagnostics;
- multi-pass ref linking into the core IR;
- group ownership of declarations during compilation;
- field/schema projection compilation;
- operation, storage, view, workflow, value-source, presentation, tag, and guidance lowering;
- canonical transport through an authoring result;
- a source adapter or direct orchestrator bridge.

Conclusion: the package is an authoring API foundation, not a usable compiler.

### 3. `codepotg-openapi`

The plugin entry point targets:

```text
codepotg_openapi.plugin:create_plugin
```

The factory imports:

```text
codepotg_openapi.adapter.OpenApiSourceAdapter
```

That module is missing on the audited branch. The adapter cannot be instantiated, and `RuntimePlugins.discover()` may fail while loading all installed source-adapter factories even for projects that select only `ir`.

Conclusion: do not install `codepotg-openapi` in the working manual environment until the facade and complete normalize pipeline are implemented and audited.

### 4. Jinja engine

The engine is suitable for the first human generation run because it provides:

- strict undefined behavior;
- in-memory declared templates and partials;
- static include/import/inheritance checks;
- bounded context and rendered output;
- cancellation;
- immutable safe records;
- restricted globals, filters, tests, attributes, and callables;
- namespaced tag query methods;
- deterministic bounded caches;
- structured diagnostics.

The manual workspace deliberately uses options, bindings, semantic naming, enum/object fan-out, tags, loops, and planner-owned export module descriptors.

### 5. TypeScript adapter

The adapter is correctly target-only. It validates TypeScript output paths and identifiers and resolves module specifiers. It does not author imports, interfaces, enums, or exports.

The direct options constructor now validates enum instances, package names, aliases, ordering, and duplicate/ambiguous roots. This addresses the recorded source audit issue.

Human acceptance requires generated files to pass a real installed TypeScript compiler.

### 6. Dart adapter

The adapter is correctly target-only. It validates Dart output paths and identifiers and resolves Dart library URI/path facts. It does not author classes, enums, constructors, or exports.

The direct options constructor now validates enum instances, package names, and Boolean package-URI preference. This addresses the recorded source audit issue.

Human acceptance requires a real Dart SDK, formatter, dependency resolution, and analyzer.

## Connectability matrix

| From | Through | To | Current result |
|---|---|---|---|
| canonical IR JSON/YAML | built-in `ir` adapter | `Contract` | Implemented; manual positive test required. |
| `Contract` | orchestrator + local pack | artifact plan | Implemented; manual positive and collision tests required. |
| artifact plan | Jinja | text artifacts | Implemented; manual positive and sandbox behavior tests required. |
| planned `.ts` paths | TypeScript adapter | module specifiers/path validation | Implemented; real compiler test required. |
| planned `.dart` paths | Dart adapter | URI/path validation | Implemented; real SDK test required. |
| memory output | managed writer | filesystem | Implemented; edit, stale, collision, rollback tests required. |
| `codepotg-author` declarations | author compiler | `Contract` | Blocked: compiler absent. |
| OpenAPI file | OpenAPI adapter | `Contract` | Blocked: adapter facade absent. |
| Git pack source | pack provider + lock | local snapshot | Planned separately; not implemented. |
| pack/project commands | approval runtime | process execution | Planned separately; intentionally fail-closed. |

## Human manual scenarios committed

The connected workspace covers:

1. exact branch confirmation;
2. clean Python environment;
3. entry-point and plugin graph inspection;
4. public IR authoring;
5. canonical JSON/YAML inspection and round trip;
6. complete plan inspection;
7. memory-only rendering;
8. real managed writes;
9. deterministic rerun hashes;
10. TypeScript compilation;
11. Dart formatting and analysis;
12. modified managed-file protection;
13. unchanged stale-file deletion;
14. unmanaged collision protection;
15. current `codepotg-author` gap reproduction;
16. current OpenAPI factory failure reproduction;
17. fresh-wheel installation rehearsal.

## Required completion order

1. Run the connected manual workspace from the exact feature head.
2. Repair any core/Jinja/target integration defects found by the human run.
3. Run synchronized Ruff, format, complete test suites, and builds for core, Jinja, TypeScript, and Dart.
4. Repeat the workspace from fresh built wheels.
5. Implement and audit `codepotg_openapi.adapter` and its complete normalize facade.
6. Add a second real manual project using OpenAPI as the source.
7. Implement the minimum complete `codepotg-author` compiler for groups, structural schemas, fields, enums, tags, guidance, and canonical transport.
8. Replace the direct-core bootstrap in a third manual scenario with `codepotg-author` while preserving identical canonical IR and generated output hashes.
9. Only then consider the entire six-package source-to-generation chain complete.

## Merge rule

Do not merge the orchestrator feature branch based only on pytest or the earlier 30-test foundation log.

Minimum merge evidence:

- exact feature-head SHA;
- all four working packages pass Ruff, format, pytest, and build;
- installed-wheel plugin discovery succeeds;
- the committed manual connected project generates all expected artifacts;
- TypeScript compilation passes;
- Dart formatting/analyzing passes or is explicitly blocked by unavailable SDK with no false pass;
- writer safety scenarios pass;
- `git status --short` is recorded and reviewed;
- unsupported OpenAPI and authoring routes remain documented honestly.
