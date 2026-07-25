---
title: Stable artifacts
 description: Learn how codepotx layers exchange deterministic, readonly, JSON-safe authoring, template, planning, rendering, manifest, and result artifacts.
product: codepotx
---

# Stable artifacts

`codepotx` layers communicate through explicit artifacts instead of sharing mutable builders, template-engine objects, filesystem handles, or CLI state. This boundary is central to reproducibility and to reusing the same engine from terminals, web tools, editors, tests, and AI integrations.

## Artifact rules

Public artifacts are designed to be:

- readonly;
- deterministic for the same inputs;
- JSON-safe;
- versioned;
- independent of one frontend;
- free of live Zod, Handlebars, process, terminal, or filesystem objects.

An artifact may contain diagnostics and provenance, but it should not contain hidden behavior.

## `CompiledAuthoringArtifact`

The authoring compiler converts the TypeScript DSL into a normalized contract artifact. It captures the semantic meaning of versions, resources, schemas, routes, entities, access policies, hooks, frontend metadata, and related references.

Consumers use the compiled artifact rather than traversing authoring builders directly.

## `CompiledTemplatePack`

The template compiler converts `paths.yaml`, templates, partials, selectors, helper requirements, lifecycle rules, and output-path expressions into a validated pack artifact.

Static validation should detect missing templates, invalid selectors, unavailable helpers, unresolved partials, unsafe output paths, and incompatible pack requirements before rendering begins.

## `TemplateVariableCatalog`

A template-variable catalog describes what a pack can read. It supports documentation, editor suggestions, inspection commands, validation, and AI tooling without rendering a template merely to discover its context.

The catalog can describe:

- variable paths;
- value kinds;
- availability and scope;
- required and optional values;
- descriptions;
- source artifact ownership.

## `GenerationPlan`

A plan is the complete intended action set for a task. It is suitable for human review and machine-readable output.

It includes planned files, output modes, dependencies, commands, cleanup actions, refusals, and diagnostics. Planning does not mutate the project.

## `RenderedGeneration`

The rendered artifact contains virtual output files after templates have executed but before the result is applied to the project. This enables previews, diff interfaces, tests, and browser or editor frontends.

## `GenerationManifest`

The manifest records task-owned managed outputs and relevant provenance. It allows stale cleanup to remove only files previously owned by the same task and only inside approved roots.

A manifest is not permission to delete arbitrary files. Cleanup still passes through current policy and platform safety checks.

## `GenerationResult`

The result summarizes the completed operation:

- created, updated, unchanged, skipped, immutable, refused, and deleted files;
- command outcomes;
- diagnostics;
- cancellation or failure information;
- transaction and rollback details;
- reports and timing information when available.

Frontends should use the result contract rather than parse terminal text.

## Artifact versioning

Artifacts need an explicit version because persisted plans, manifests, caches, editor state, and integrations may outlive one package build. A consumer should reject or migrate unsupported artifact versions instead of guessing.

## Why this matters for AI and tools

Structured artifacts let tools inspect software intent without repeatedly rediscovering repository conventions from source text. An AI client can request a plan, variable catalog, or compiled contract and receive bounded, typed information rather than unrestricted filesystem access.

## Public import boundary

Artifact types are exposed through supported package entrypoints such as:

```ts
import type {
  CompiledAuthoringArtifact,
  GenerationPlan,
  GenerationResult,
} from "codepotx/contract";
```

Do not import private implementation files. Internal folder paths are not a compatibility boundary.

## Related pages

- [Architecture](/docs/packages/codepotx/architecture)
- [Generation](/docs/packages/codepotx/generation)
- [Runtime and platform services](/docs/packages/codepotx/runtime-platform)
