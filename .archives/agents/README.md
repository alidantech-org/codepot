# Codepot project guide

Codepot is a TypeScript-first authoring, templating, and source-generation system. The active implementation is `packages/nodejs/codepotx`; the previous Node implementation is preserved in `packages/nodejs/codepotx-old`, and the deprecated Python generator remains in `packages/python/codepotg` as a behavior reference.

## Product model

Codepot has three autonomous layers:

1. **Authoring** loads `codepotx.config.ts`, executes only its reachable TypeScript authoring graph, validates the definitions, and produces a stable serializable `CompiledAuthoringArtifact`.
2. **Templating** loads and validates `paths.yaml`, discovers Handlebars templates and static files, compiles the template pack, and builds deterministic template contexts from the authoring artifact.
3. **Generation** loads `CodepotFile.yml`, resolves selected authoring and template sources, plans output, renders in memory, applies lifecycle and safety rules, writes through an injected writer, and runs approved before/after commands.

A shared contract defines artifacts, requests, results, events, diagnostics, engine ports, and platform ports. Runtime composes implementations and exposes them to frontends. The CLI is a separate package and only one possible frontend.

## User-facing compatibility

Existing TypeScript authoring contracts must retain their behavior, fluent builders, generic inference, refs, metadata, validation, and generated meaning. The expected migration is primarily:

```ts
import {
  defineVersionContract,
  schema,
  z,
} from 'codepotx';
```

Users do not install Zod. `codepotx` owns it internally and exports a curated Codepot schema surface plus a `z` compatibility namespace.

## Sources of truth

- `agents/ARCHITECTURE.md` — top-level module boundaries and dependency direction.
- `agents/CODEPOTX_STRUCTURE_GUIDE.md` — required scalable folder/file structure, chunking rules, type-safety invariants, and non-breaking migration method.
- `agents/RULES.md` — clean-code, compatibility, and dependency rules.
- `agents/WORKFLOW.md` — issue, task, implementation, validation, and commit workflow.
- `agents/FEATURES.md` — required product behavior.
- `agents/tasks/00-roadmap.md` — ordered project status.
- `agents/tasks/15-codepotx-structure-migration.md` — umbrella record for the structural migration program.
- `packages/nodejs/codepotx-old` — TypeScript authoring and compiler behavior reference.
- `packages/python/codepotg` — CodepotFile, paths, template-context, planning, writing, cleanup, command, and reporting behavior reference.

## Work order

Implementation proceeds in this order:

1. shared contracts and stable artifacts;
2. runtime and platform adapters;
3. authoring compatibility and canonical compilation;
4. templating and Handlebars migration;
5. generation and CodepotFile orchestration;
6. external CLI;
7. full parity, packaging, and release validation;
8. structure hardening through Tasks 15-23 before further large-scale feature expansion.

The structure migration must begin with Task 16 baseline and architecture guardrails. Do not perform broad file moves before those checks exist.
