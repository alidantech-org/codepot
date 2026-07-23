# Task 17 — Contract partitioning and protocol ownership

Status: [~]
Issue: #15 open
Depends on: Task 16 complete
Commits: structural checkpoint from `646e02620f3f0dddb1b7e94913567e1edd168a10` through `0a35d951b756e1f311fb5da236d04a2409ba8269`; inventory `6ea901c9a71da0e9d4530b5e72e2bde70a8e6b3d`; guardrails `f5f574a3d9256b41c13fce1ff95ae2494f0da320`, `8eae32ff04967b9ae0cacc70f7232c8d2aafacd8`; isolated declaration fix `9168f681f321c6e8406f361d0524b4df7dfaf977`
Validation: strict source and test typecheck passed after the explicit producer metadata annotation. Full behavioral, declaration, architecture, build, and package validation is pending.

## Goal

Replace the broad contract type warehouse with focused protocol, artifact, operation, port, diagnostic, event, and source modules while preserving every public contract export and serialized field meaning.

## Target structure

```text
src/contract/
├── protocol/
├── artifacts/
│   ├── authoring/
│   ├── templating/
│   └── generation/
├── operations/
│   ├── authoring/
│   ├── templating/
│   ├── generation/
│   └── runtime/
├── ports/
├── diagnostics/
├── events/
├── sources/
└── index.ts
```

## Work

- [x] Inventory every exported contract symbol and current import path in `agents/audits/CODEPOTX_CONTRACT_INVENTORY.md`.
- [x] Move protocol versions and artifact header contracts into `protocol/`.
- [x] Group authoring, template, generation-plan, rendered-generation, manifest, and result artifacts by owner.
- [x] Split request/result mappings by operation layer.
- [x] Split infrastructure ports into focused files.
- [x] Split engine ports into focused files.
- [x] Move diagnostics, events, and source descriptors into owned folders.
- [x] Keep compatibility re-exports at `codepotx/contract` during migration.
- [x] Replace contract-internal broad imports with focused type-only imports.
- [x] Introduce one typed package-version source at `src/internal/package-info.ts`. Adoption by authoring, templating, and generation artifact assemblers is assigned to Tasks 18–20 when those assemblers are extracted from their current monoliths.
- [x] Split common protocol primitives from diagnostic operation-result definitions without changing their meaning.

## Type-safety requirements

- [x] Preserve the runtime operation request/result type mapping under strict typecheck.
- [x] Preserve discriminated unions and exhaustive artifact kinds under strict typecheck.
- [ ] Preserve readonly and JSON-safe artifact contracts against the baseline suite.
- [x] Add a contract-specific circular-import guardrail.
- [x] Add a contract guardrail that rejects external, Node, platform, and domain implementation imports.

## Acceptance criteria

- [x] Existing root and `codepotx/contract` consumer type fixtures compile unchanged.
- [ ] Artifact JSON snapshots match the baseline.
- [ ] Declaration output contains no private implementation paths.
- [ ] Architecture checks confirm `contract` depends on no internal Codepot layer.
- [ ] Public export snapshot changes are intentional and reviewed.

## Producer metadata handoff

- Task 18 adopts `CODEPOT_ARTIFACT_PRODUCER` in authoring artifact assembly.
- Task 19 adopts it in template-pack and template-variable artifact assembly.
- Task 20 adopts it in generation-plan, rendered-generation, and manifest assembly.
- Producer name and version remain `codepotx` and `0.0.0`; this handoff does not change protocol or serialized values.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```
