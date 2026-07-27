# Parallel work registry

This file coordinates implementation across conversations. Claim a task before changing implementation files.

## Active claims

| Task ID | Package/subsystem | Owner/chat | Status | Expected files | Dependencies | Notes |
|---|---|---|---|---|---|---|
| CORE-001..CORE-006, PATH-001, IR-001..IR-010, SOURCE-001, PLUG-001 public contracts | `codepotg-v2` organized foundation, closed IR, and adapter ports | current ChatGPT implementation session | in_progress | `pyproject.toml`; `src/codepotg/api/**`; `diagnostics/**`; `domain/ir/**`; `domain/generation/**`; `plugins/**`; `ports/**`; `testing/**`; public facades; mirrored unit/contract/architecture/distribution tests; task/progress evidence | DOC-001..DOC-007 | The rejected flat implementation has been replaced by the approved package structure. Packaging, tests, lint, and build are under corrective verification. No planner, writer, CLI behavior, or compatibility runtime is included. |
| OA-001..OA-008, OA-016..OA-018 | `codepotg-openapi` package/plugin, options, controlled loading, parsing, references, standard normalization, provenance, digest, conformance | ChatGPT OpenAPI implementation session (`chatgpt/codepotx-restart-codepotg-openapi`) | claimed | `packages/python/codepotg-openapi/pyproject.toml`; `README.md`; `src/codepotg_openapi/**`; `tests/{architecture,contracts,distribution,integration,performance,unit}/**`; `benchmarks/**`; `docs/tasks/PROGRESS.md` | published `codepotg.api`, `codepotg.diagnostics`, `codepotg.ir`, `codepotg.plugins`, `codepotg.ports`, `codepotg.testing`, `codepotg.versions` at base `686d8a9c` | No blockers at claim time. Default adapter authority is memory/local-only with local containment; unsupported public-IR facts will be bounded and diagnosed. Test evidence will be appended per coherent batch. |
| JINJA-001..JINJA-007, JINJA-009..JINJA-011 | `codepotg-template-jinja` safe Jinja template-engine adapter | GPT-5.6 Thinking / CODEPOT session 2026-07-27 | in_progress | `packages/python/codepotg-template-jinja/pyproject.toml`; `README.md`; `LICENSE`; `src/codepotg_template_jinja/**`; `tests/**`; `benchmarks/**`; `docs/tasks/PROGRESS.md`; package-local ignore/support documentation | Current public `codepotg.ports.TemplateEngine`, `RenderRequest`, `RenderResult`; public diagnostics, cancellation, plugin/version, IR, and conformance namespaces at base `686d8a9c` | Feature branch `chatgpt/codepotx-restart-codepotg-template-jinja` is the compatible form because Git cannot create a branch nested below existing ref `chatgpt/codepotx-restart`. Named outputs (`JINJA-008`) remain blocked because a public planner-declared named-output request/result contract is required. Full pack-registry/target-compatible partial validation, project/pack engine-rule decoding, and runtime cache-port integration remain blocked by missing public core contracts. No private core imports or compatibility protocols will be added. |
| TS-001..TS-010, DART-001..DART-010 | coordinated TypeScript and Dart target-language adapters | current ChatGPT implementation session | review | `packages/python/codepotg-language-typescript/**`; `packages/python/codepotg-language-dart/**`; coordination updates in this file only | current public CodepotG `TargetAdapter` protocol | Merged through PR #30 from `chatgpt/codepotx-restart-language-adapters`. Both complete package suites passed in the local public-contract harness, so the coordinated claim remains in review rather than complete. The adapters remain separate independently installable distributions and do not import one another. TS-009/DART-009 remain blocked on official pack/planning contracts; final completion remains blocked on the exact core, Ruff, build, real-wheel, and Dart-SDK verification commands. No core implementation file was modified. |

## Parallel package lanes available through public contracts

The following package-local tasks may be claimed in separate conversations without editing `packages/python/codepotg-v2/src/codepotg/**`:

| Package | Tasks that may begin | Public contracts available |
|---|---|---|
| `codepotg-openapi` | OA-001 package foundation, OA-002 adapter entry point, typed normalization work beginning from schemas/groups/operations | `codepotg.ir`, `codepotg.diagnostics`, `codepotg.ports.SourceAdapter*`, `codepotg.testing.assert_source_adapter_conformance` |
| `codepotg-language-typescript` | TS-001 foundation through target descriptor/identifier/path validation scaffolding | `codepotg.plugins`, `codepotg.ports.TargetAdapter`, target/path request and result types, target conformance helper |
| `codepotg-language-dart` | DART-001 foundation through target descriptor/identifier/path validation scaffolding | same public target contracts as TypeScript |
| `codepotg-template-jinja` | Jinja package foundation, immutable render request/result, deterministic engine scaffolding | `codepotg.ports.TemplateEngine`, `RenderRequest`, `RenderResult`, engine conformance helper |
| `codepotg-author` | AUTHOR-001..AUTHOR-013, AUTHOR-015..AUTHOR-020 current subset, AUTHOR-022, AUTHOR-024, AUTHOR-027..AUTHOR-030 | public `codepotg.ir`, diagnostics, naming, versions, and validation facades; missing tags/guidance/field-capability/value-source/presentation contracts remain exact core blockers |

These lanes may depend only on published modules. They must not import `codepotg.domain`, mutate the kernel, or copy private implementation classes. Until the corrective verification passes, parallel packages should pin to a specific core commit and treat API changes as possible foundation repairs rather than stable-release changes.

## Planned task lanes

| Lane | Task range | Primary ownership | May start when |
|---|---|---|---|
| Core primitives | CORE-001..CORE-006 | `codepotg-v2` | documentation accepted |
| Semantic naming/expressions | PATH-001..PATH-003 | core naming/path contracts | core version and diagnostics available |
| Configuration | CFG-001..CFG-006, PACKCFG-001..PACKCFG-005 | `codepotg-v2/config` | core diagnostics available |
| Closed semantic kernel | IR-001..IR-010 | domain/IR and validators | core primitives and PATH-001 stable |
| Root-first selectors/selection folders | PLAN-002..PLAN-004, PATH-004, PATH-006 | generation/config/IR contracts | typed config and kernel stable |
| Filesystem discovery/path planning | PLAN-001, PLAN-003..PLAN-010, PATH-005, PATH-007..PATH-010 | generation domain/application | pack config, expressions, selectors, and IR stable |
| Generated dependencies/path facts | BIND-002, PLAN-006..PLAN-007, PATH-008 | semantic artifact graph + target path ports | selections, artifacts, destinations, and symbols stable |
| Explain and impact | PLAN-010..PLAN-011 | planner/inspection API | semantic and artifact plans stable |
| Conservative incremental generation | PLAN-012 | planner/cache/state | deterministic full generation and impact graph proven |
| Plugin runtime | PLUG-001..PLUG-011 | plugins/ports/runtime | public primitives and closed-kernel boundary stable |
| Writers/cache/state | WRITE/CACHE tasks | infrastructure + ports | artifact/path plan stable |
| Commands/setup | CFG-004..CFG-005, CMD, SETUP/CONFIGURE/ECO | application/infrastructure | config/security contracts stable |
| Python API/CLI | API/CLI/MCP and impact API | api/application/cli | core use cases stable |
| Local/Git distribution | GIT/LOCK/DIST | pack provider/lock/cache | direct source and pack manifest contracts stable |
| OpenAPI adapter | OA-001..OA-020 | `codepotg-openapi` | closed IR/source port stable |
| Python authoring compiler | AUTHOR-001..AUTHOR-030 | `codepotg-author` | public closed IR and validation stable; each blocked semantic addition requires a separate approved kernel task |
| TypeScript target adapter | TS-001..TS-010 | `codepotg-language-typescript` | target validation/path port and PLAN-007 stable |
| Dart target adapter | DART-001..DART-010 | `codepotg-language-dart` | target validation/path port and PLAN-007 stable |
| Jinja engine | JINJA tasks | `codepotg-template-jinja` | engine port/immutable context stable |
| Official packs | PACK-TS/PACK-DART/PACK-FLUTTER | pack packages | simplified manifest, closed kernel, PATH/PLAN, target adapters, and engine stable |
| Connected system fixture | PACK-SYSTEM, TEST-003..TEST-005 | cross-package integration | official adapters/packs and impact plan stable |

## Claim procedure

1. Select an unclaimed task whose dependencies are complete.
2. Add a row under Active claims with status `claimed`.
3. List expected files narrowly. Do not claim an entire package for a small task.
4. Change status to `in_progress` in the first implementation commit.
5. Move to `review` after implementation and tests.
6. Mark `complete` only after acceptance criteria and the complete verification command set pass.
7. Remove completed claims only after the completion record exists in `PROGRESS.md`.

## Active claim row format

| Task ID | Package/subsystem | Owner/chat | Status | Expected files | Dependencies | Notes |
|---|---|---|---|---|---|---|
| CORE-001 | package foundation | chat identifier | claimed | package metadata/import tests only | DOC-001..DOC-007 | Example only; remove when making a real claim. |

## Conflict rule

Two agents must not edit the same implementation file concurrently. Closed-kernel, selector, path/name, dependency, IR, validation, plugin, and render-context contracts require narrow ownership because adapters and packs depend on them.

## Design gates

- Core alone owns semantic objects, relations, schema kinds/roles, known facets, root-first selectors, expression roots, template contexts, and semantic validation.
- Source adapters normalize only into the known kernel and cannot register semantic extensions.
- The Python authoring compiler may be expressive, but it compiles only into public core IR; Pydantic, author refs/builders, and Python callables never enter IR or template contexts.
- Tags, categorized guidance, field capabilities, value sources, presentations, and canonical transport additions require intentional typed core contracts when they must be visible beyond authoring; they cannot be hidden in arbitrary extensions or private author IR.
- Packs use filesystem discovery, registered `{selectionKey}` folders, fixed root-first selectors, `(expression)`, explicit imports/exports/symbols, and pack-relative `paths` arrays.
- Templates, macros, partials, and static files own every emitted character.
- Target adapters validate targets/names and calculate module/path facts; they do not render types, literals, comments, imports, exports, validators, decorators, formatting, or framework code.
- No implementation may restore flat source/test dumps, neutral resource/model/entity/frontend/UI roots, reversed selectors, arbitrary query/traversal DSLs, profiles, or `filePatterns`.
- Git provider work implements direct `source.local`/`source.git` and must not introduce registries, `use`, or GitHub-only locators.
- Command work preserves exact opaque arguments and does not infer installation syntax from dependency metadata.
- Output hashes/state belong to ownership/generation state, not the dependency lock.
- Incremental generation begins only after deterministic full generation and impact analysis are proven.

## Blockers

A blocked task records the exact dependency task ID and missing contract/artifact. Generic notes such as “waiting for core” are insufficient.
