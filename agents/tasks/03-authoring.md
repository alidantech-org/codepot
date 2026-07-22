# Phase 03 — Authoring parity and canonical compiler

Status: [ ]
Issue: open when required Phase 01/02 ports are complete
Depends on: Shared contracts, module loader, source resolver, cache, hashing, diagnostics, events
Commit: pending
Validation: pending

## Goal

Preserve old TypeScript authoring behavior tooth by tooth while compiling user contracts directly into the stable Codepot authoring artifact.

## 03.1 Compatibility inventory

- [ ] Inventory every old root runtime export and type export.
- [ ] Inventory every builder method, overload, generic inference rule, ref, enum, error, validation rule, and metadata field.
- [ ] Add real old contracts as compatibility fixtures with import-only migration.
- [ ] Capture old validation and semantic-output snapshots before porting.

## 03.2 Public authoring surface

- [ ] Port properties, schemas, refs, components, versions, resources, routes, entities, relations, access, hooks, frontends, info, and metadata in dependency order.
- [ ] Keep interface/type declarations separate from implementations.
- [ ] Export `schema` as the preferred curated namespace.
- [ ] Export `z` as the compatibility namespace from `codepotx`.
- [ ] Keep Zod internal and prevent Zod objects from entering stable artifacts.

## 03.3 Config loading

- [ ] Define `CodepotConfig` and `defineCodepotConfig` contracts before implementation.
- [ ] Load `codepotx.config.ts` using the consumer TypeScript configuration and reachable import graph only.
- [ ] Support user aliases without building the whole application.
- [ ] Support optional old `package.config.ts` and `definePackageConfig` compatibility with diagnostics.
- [ ] Support source mode, cache mode, and precompiled artifact mode.

## 03.4 Canonical compilation

- [ ] Extract validation and compiler passes from the old OpenAPI-centered compiler.
- [ ] Resolve registries, refs, usage metadata, entities, resources, operations, access, hooks, and frontends.
- [ ] Normalize to deterministic `CompiledAuthoringArtifact`.
- [ ] Provide inspect/debug serialization using the same stable artifact contract.
- [ ] Keep any OpenAPI compatibility projection outside the required authoring-to-generation path.

## 03.5 Validation

- [ ] Old fixtures compile after import-only migration.
- [ ] Fluent chains and inferred types remain compatible.
- [ ] Canonical artifacts are deterministic and serializable.
- [ ] Validation issues and source locations are stable.
- [ ] Cache invalidation follows the reachable source graph.
- [ ] Typecheck, tests, build, and package validation pass.
- [ ] Record issue, commit, and evidence before marking complete.
