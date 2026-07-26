# TypeScript SDK tokenized path-authoring tasks

## PACK-TS-PATH-001 — Author physical tokenized source tree

**Dependencies:** PATH-001..PATH-010, TypeScript target descriptor

- [ ] Place model templates under a path such as `{models}/[model.name.kebab.s].model.ts.jinja`.
- [ ] Place operation/action templates under `{actions}/[operation.name.kebab.o].action.ts.jinja`.
- [ ] Place authored barrels under structural root recipes such as `{generatedRoot}/index.ts.jinja`.
- [ ] Place static `.gitignore`, `.env.example`, ESLint, package, and documentation files under the same named recipes.
- [ ] Use literal `[[...slug]]` escaping in any Next.js-style route fixture.
- [ ] Do not add explicit output paths for ordinary descriptors.

## PACK-TS-PATH-002 — Declare paths and name policy usage

- [ ] Declare structural and selection-bearing recipes under `CodepotgPack.yaml` `paths`.
- [ ] Use explicit case and original/singular/plural projections in source names.
- [ ] Document why each `.o`, `.s`, or `.p` choice is used.
- [ ] Keep TypeScript adapter filename validation separate from pack path composition.

## PACK-TS-PATH-003 — Conformance

- [ ] Test tokenized model, enum, DTO, operation, client, test, docs, static, and authored barrel paths.
- [ ] Test irregular names, acronyms, plural source names, collisions, and case-insensitive destinations.
- [ ] Test modular and monolithic profiles.
- [ ] Prove source-path inspection explains every output.
- [ ] Prove no semantic fixture exposes `fileName`, `filePath`, or `directory`.

**Acceptance:** the realistic TypeScript SDK fixture generates solely from source paths, named recipes, typed values, and the project output root.
