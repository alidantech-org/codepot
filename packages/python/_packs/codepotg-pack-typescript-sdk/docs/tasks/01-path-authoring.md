# TypeScript SDK selection-folder authoring tasks

## PACK-TS-PATH-001 — Author the physical template tree

**Dependencies:** PATH-001..PATH-010, TypeScript target descriptor

- [ ] Place models under `{models}/(model.name.kebab.s).model.ts.jinja`.
- [ ] Place DTOs, enums, services, and clients under their registered selection folders.
- [ ] Place barrels under selections that declare ordered `exports`.
- [ ] Keep package files, documentation, and static content literal and unregistered.
- [ ] Use `.gitignore.jinja` when the generated package needs a `.gitignore`.
- [ ] Use literal bracket routes and `((admin))` for literal parenthesized route groups.

## PACK-TS-PATH-002 — Declare compact selections

- [ ] Use one `selections` mapping with pack-relative `paths` arrays.
- [ ] Use fixed selectors such as `schemas.models.each`, `schemas.dtos.each`, `schemas.enums.each`, and `resources.each`.
- [ ] Declare generated dependencies with `imports: localName: selectionKey`.
- [ ] Declare barrels with `exports: [selectionKey]` and all generated symbols explicitly.
- [ ] Use `(name.case.number)` expressions in physical filenames.
- [ ] Do not add root `paths`, `files`, `filePatterns`, arbitrary `from`/`as`, or explicit ordinary output paths.

## PACK-TS-PATH-003 — Conformance

- [ ] Load `codepotg-v2/docs/examples/packs/typescript-sdk.CodepotgPack.yaml` as the baseline fixture.
- [ ] Test model, enum, DTO, service, client, barrel, docs, static, and partial discovery.
- [ ] Test direct versus barrel imports and least-required symbols.
- [ ] Test irregular names, acronyms, plural source names, collisions, and case-insensitive destinations.
- [ ] Prove path inspection explains every output and dependency.
- [ ] Prove no semantic fixture exposes `fileName`, `filePath`, or `directory`.

**Acceptance:** the TypeScript SDK generates from its filesystem, compact selections, fixed selectors, explicit dependencies, and project output root.
