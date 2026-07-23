# Task 23 — Full structural migration integration gate

Status: [~]
Issue: #21 open
Depends on: Tasks 16–20 complete; Tasks 21–22 implementation complete
Commits: final audit `324004ab4a20edc2a5bb29675d5af7c48d69f285`; integration guardrail `cbe7b62394d186a923a790b0e804ffcf48e318f3`, `bedf0726dc6d67dc4c17868daf93fc52378f3bf1`; grouped architecture wiring `81839d6ba1700ece7fb3f5a0d7602787399f9192`; final public-facade reconciliation through `116facc1ae17876fc36798e98965d7b24f38efb5`; task evidence update `85f44b40d01ce80ad5c57015d80a8cd615e12886`; isolated declaration fix `e90283a1d1d0a364bd570305c427c0d9c69f7a55`; generic consumer fixture fix `fb6904b2b67a84ed70d0066ede8c533f5284e556`; site TypeScript compatibility fix `0753a0b337d547cf533fa20eff7929e9716692fd`; site lint and generated-file cleanup through `f4025087716d191f346d3c46a6b54ce51b41fe11`
Validation: CodepotX passed strict source/test typechecks, 56/56 tests, declaration build, Publint, and ESM package-resolution checks. CodepotX CLI passed strict source/test typechecks, 3/3 tests, build, Publint, and ESM package-resolution checks. The site now passes TypeScript 6 typecheck and a complete production build. The remaining workspace blocker is site lint; commits through `f4025087716d191f346d3c46a6b54ce51b41fe11` remove the four lint errors and warning, and stop tracking generated `next-env.d.ts`. The regenerated `pnpm-lock.yaml`, site lint, workspace check, and clean workspace build remain required before Tasks 15, 21, 22, and 23 and issues #19–#21 can close.

## Goal

Prove that the completed folder and file migration is behaviorally equivalent, type-safe, package-safe, and ready for continued feature development.

## Structural audit implementation

- [x] Compare the final package tree with `agents/CODEPOTX_STRUCTURE_GUIDE.md` and record it in `agents/audits/CODEPOTX_STRUCTURE_FINAL.md`.
- [x] Add facade-size checks for authoring compiler/engine, templating, generation, runtime, and platform composition.
- [x] Confirm capability folders own implementation and migrated flat platform modules are thin shims.
- [x] Confirm no mixed source-resolver ownership remains.
- [x] Confirm dependency-boundary tests cover contract, internal, authoring, templating, generation, platform, and runtime.
- [x] Confirm public entrypoints contain explicit curated exports and no application/pass/dispatch internals.
- [x] Confirm grouped suites reach every original behavior suite exactly once.
- [x] Confirm documentation and task records are present and current.

## Behavioral equivalence coverage

- [x] Authoring artifacts are compared with the Task 16 baseline.
- [x] Compiled template packs are compared with baseline fixtures.
- [x] Template context, variable catalogs, strict validation, and rendered files are covered.
- [x] Generation plans, files, manifests, cache keys, reports, and diagnostics are covered.
- [x] Managed, immutable, protected, cleanup, command, transaction, rollback, dry-run, cancellation, cache, and event behavior are covered.
- [x] Real old-style TypeScript compatibility contracts are included.
- [x] Shared Python-compatible template context behavior is covered where intentionally ported.
- [x] CLI request mapping and frontend-only presentation remain covered by CLI tests.

## Type and package validation implementation

- [x] Public generic inference and every package subpath are imported by `tests/public-entrypoints.fixture.ts`.
- [x] Runtime value surfaces are snapshot-tested.
- [x] Public package keys remain unchanged.
- [x] Public wildcard exports are rejected.
- [x] Runtime operation registration is exhaustive and cast-free at the dispatch boundary.
- [x] Node and memory adapter parity remains in the complete suite.
- [x] The explicit contract and root type facades match the Task 17 symbol inventory, including `CompiledPathToken`.
- [x] Add the explicit exported property annotation required by `isolatedDeclarations` for `CodepotCancellationController.signal`.
- [x] Instantiate generic `ArtifactHeader` with a valid artifact kind in the public consumer fixture.
- [x] Keep CodepotX and CLI on TypeScript 7 while providing the site tooling with the TypeScript 6 compatibility API.
- [x] Strict source/test typecheck and declaration generation pass for CodepotX and CLI.
- [x] Publint and Are The Types Wrong pass for CodepotX and CLI.
- [x] Site TypeScript check and production build pass with the package-local TypeScript 6 compatibility compiler.
- [ ] Site lint and the complete workspace check must pass after pulling the lint fixes.
- [ ] Commit the regenerated TypeScript-alias lockfile and confirm the final workspace build remains clean.

## Full validation

```bash
pnpm --filter codepotx check
pnpm --filter codepotx-cli check
pnpm check
pnpm build
```

The package suite includes dry-run and temporary real-write generation behavior through memory and temporary Node adapters.

## Completion criteria

- [ ] Tasks 16–22 are complete with closed issues and validation evidence.
- [ ] All commands and behavioral comparisons pass.
- [x] Final package tree and compatibility-shim policy are documented.
- [x] No unresolved migration exception remains.
- [ ] Task 15 is marked complete after the final gate.
- [ ] Issue #21 closes only after the final validation evidence is committed.
