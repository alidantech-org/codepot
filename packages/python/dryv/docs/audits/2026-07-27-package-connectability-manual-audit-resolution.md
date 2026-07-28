# Dryv package connectability and human-validation audit resolution

Date: 2026-07-27

Audited branch:

```text
chatgpt/codepotx-restart-orchestrator
```

Latest base synchronization merge:

```text
1354943069121a2e7e8ec4e2a85ec6ef36f9855f
```

## Executive result

All six v2 Python packages now have enough implementation to attempt one connected human workflow:

```text
public IR Python -----------> core canonical JSON/YAML --+
                                                        |
dryv-author -> Contract -> core canonical JSON/YAML -+-> orchestrator
                                                        |      -> local packs
standard OpenAPI -----------> OpenAPI source adapter ----+      -> Jinja
                                                               -> TypeScript/Dart adapters
                                                               -> managed files
                                                               -> real target tools
```

This is an **audit-ready candidate**, not a completed release claim. The connected project must still be run from the exact synchronized branch and then repeated from freshly built wheels.

Committed human workspace:

```text
packages/python/dryv/examples/manual/connected-project
```

## Supplied core log

The user-supplied Windows log proves the earlier core foundation passed Ruff, format, 30 tests, and package build. Its wheel contents do not contain the later orchestrator configuration, planner, runtime, CLI, codec, or managed-writer modules. It must therefore remain foundation evidence rather than evidence for the current connected runtime.

## Current package status

| Package | Current implementation | Connectability now | Remaining acceptance |
|---|---|---|---|
| `dryv` / `dryv` | Full first local-pack orchestrator path implemented on this branch. | Connects strict project config, `ir`/OpenAPI sources, local packs, Jinja, target adapters, memory output, archive output, and managed filesystem output. | Run synchronized Ruff/format/tests/build, the committed human project, and fresh-wheel repetition. |
| built-in `ir` source adapter | Implemented and registered by core. | Positive route from core canonical JSON/YAML to `Contract`. | Verify installed-wheel discovery and all three human source routes. |
| `dryv-author` | Typed declarations, Pydantic compilation, projections, semantics, public `Contract` compiler, and tests implemented. | Positive route through `Author.compile().contract` and the core canonical codec. | Run author pytest/mypy/pyright/build/wheel; unify or remove duplicate package-local transport. |
| `dryv-openapi` | Public adapter, isolated loading session, bounded parser, resolver, standard schema/group/operation normalization, diagnostics, conformance/security/integration/distribution tests implemented. | Positive standard OpenAPI route to a public `Contract`. | Reproduce synchronized Ruff/format/tests/build/wheel; keep security and typed `x-codegen` claims explicitly unsupported. |
| `dryv-template-jinja` | Release-verified for the current `TemplateEngine` port. | Positive render route for immutable prepared contexts, declared partials, tags, options, bindings, imports, and exports. | Connected orchestrator human run; future named-output/cache-port work remains separate. |
| `dryv-language-typescript` | Release-verified for the current `TargetAdapter` port, including real TypeScript compiler oracle and wheel-only discovery. | Positive output validation and module-specifier route for `.ts`/`.tsx` artifacts. | Compile all three generated manual projects through the official orchestrator. |
| `dryv-language-dart` | Release-verified for the current `TargetAdapter` port, including real Dart SDK oracle and wheel-only discovery. | Positive output validation and URI/module-path route for `.dart` artifacts. | Format/analyze all three generated manual projects through the official orchestrator. |

## High-severity cross-package finding: duplicate IR transport

`dryv-author` owns a second transport codec with this envelope:

```text
format: dryv.ir
version: 1
```

Core owns the canonical transport consumed by the built-in `ir` source adapter. These are not the same contract, and the author codec's fixed registry does not cover all newer core IR types such as tags, guidance, field capabilities, value sources, and presentations.

Required rule until repaired:

```text
Author.compile()
    -> AuthoringResult.contract
    -> dryv.ir.contract_to_json / contract_to_yaml
    -> built-in ir source adapter
```

Do not use `dryv_author.dumps_json()` as an orchestrator source file. Recommended repair: make `dryv-author` delegate transport entirely to the public core codec and remove its duplicate schema registry.

## OpenAPI support boundary

The public `OpenApiSourceAdapter` now produces core-valid immutable contracts for the implemented standard subset and owns isolated loading/reference state per normalization call.

Currently valid human input includes:

- OpenAPI 3.0/3.1 document metadata;
- local files and bounded local references;
- component schemas;
- groups/tags;
- standard operations, parameters, outputs, failures, and local schema references within the implemented normalization subset.

Currently not typed semantic support:

- security schemes/application semantics;
- typed `x-codegen`;
- the remaining OA-009..OA-015 advanced semantics.

These inputs must emit truthful diagnostics and may be preserved as bounded raw source data. Preservation is not implementation.

## Human routes committed

### Route A — direct core IR

```text
bootstrap_contract.py
-> contract.codepot.json / contract.codepot.yaml
-> dryv.yaml
-> runs/direct
```

Tests tags, guidance, constraints, core codec round trip, fixed selectors, two target packs, generated barrels/libraries, and writer state.

### Route B — Python authoring

```text
bootstrap_author_contract.py
-> Author.compile()
-> core canonical codec
-> dryv-author.yaml
-> runs/author
```

Tests typed refs/declarations, public IR compilation, core transport bridge, and the same two packs.

### Route C — OpenAPI

```text
openapi.yaml
-> OpenApiSourceAdapter
-> dryv-openapi.yaml
-> runs/openapi
```

Tests installed source-adapter discovery, standard normalization, the same planner and packs, and target generation.

## Human acceptance beyond pytest

The workspace requires a person to perform and inspect:

1. clean installation of all six packages;
2. exact entry-point enumeration and plugin loading;
3. direct IR JSON/YAML inspection;
4. Python authoring compilation and transport inspection;
5. OpenAPI normalization and diagnostic inspection;
6. dry-run artifact plans for all three routes;
7. memory rendering with no filesystem mutation;
8. managed generation into isolated destinations;
9. target-language source review;
10. TypeScript compilation for all routes;
11. Dart formatting/analyzing for all routes;
12. deterministic regeneration hash comparison;
13. modified managed-file protection;
14. unchanged stale-file deletion;
15. unmanaged collision protection;
16. explicit unsupported OpenAPI semantics probe;
17. Git-pack and command fail-closed probes;
18. builds of all six packages;
19. complete repetition from wheels only;
20. final clean-tree review.

## Completion decision

### Can be called complete for the current isolated port

- Jinja template engine package.
- TypeScript target adapter package.
- Dart target adapter package.

Their package-level release evidence exists, while official end-to-end pack rendering is now tested through this manual candidate.

### Implemented but still in review

- Core/orchestrator branch.
- Built-in core IR adapter.
- `dryv-author` compiler.
- `dryv-openapi` standard adapter.

### Still separate or blocked lanes

- Git pack provider, immutable lock resolution, and offline snapshots.
- Project/pack command approval and execution runtime.
- Full cache/impact/incremental generation.
- OpenAPI security and typed `x-codegen` semantics.
- Advanced authoring for all newly added core semantics.
- One authoritative shared canonical transport across core and authoring.

## Merge gate

Do not merge the orchestrator branch based on package pytest alone.

Minimum evidence:

```text
[ ] exact synchronized branch SHA
[ ] core Ruff, format, full tests, and build
[ ] author Ruff, format, full tests, mypy, pyright, and build
[ ] OpenAPI Ruff, format, full tests, and build
[ ] Jinja/TypeScript/Dart release evidence still matches current dependencies
[ ] six-package editable plugin graph
[ ] direct IR manual route passed
[ ] Python author manual route passed
[ ] standard OpenAPI manual route passed
[ ] all generated TypeScript projects compiled
[ ] all generated Dart projects analyzed, or SDK absence recorded honestly
[ ] deterministic and writer-safety scenarios passed
[ ] all six wheels installed together in a fresh environment
[ ] wheel-only repetition passed
[ ] final git status reviewed
```
