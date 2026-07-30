# Task 26 — CodepotG `paths.yaml` graph completion

Status: [-]
Branch: `chatgpt/codepotx-restart`
Depends on: Task 25 typed template-variable contract

## Goal

Complete the approved selection/emission graph so `paths.yaml` connects source selections, output paths, explicit providers, imports, barrels, lifecycle policy, and bounded lazy contexts without breaking legacy folder packs.

## Required work

- [ ] Validate named selections and emissions independently.
- [ ] Support one-item, all-items, and per-resource grouped selection scopes.
- [ ] Support schemas, primitives, DTOs, enums, entities, operations, paths, resources, access definitions, frontends, and supported component collections.
- [ ] Allow one source selection to feed multiple emissions.
- [ ] Register every planned output before physical writing.
- [ ] Resolve dependencies only through explicit configured providers.
- [ ] Validate effective provider conflicts, including transitive barrel exports.
- [ ] Schedule barrels as graph nodes after their declared members are written.
- [ ] Expose direct-file and barrel import facts through typed file context.
- [ ] Stream selected, resolved, planned, rendering, queued, written, unchanged, immutable-skipped, refused, failed, and completed events.
- [ ] Preserve legacy folder-pack behavior during migration.
- [ ] Add migration fixtures that generate the same representative outputs through legacy and graph paths.

## Safety constraints

- Do not infer providers from source availability.
- Do not weaken duplicate-path, unsafe-write, traversal, cycle, or missing-provider failures.
- Do not require a global full-project render barrier.
- Do not place large source or dependency indexes in `manifest.json`.

## Validation

- [ ] Graph configuration tests pass.
- [ ] Provider/barrel conflict and scheduling tests pass.
- [ ] Legacy compatibility tests pass.
- [ ] Realistic pack tests pass.
- [ ] Complete package suite passes.
