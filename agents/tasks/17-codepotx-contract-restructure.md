# Task 17 — Contract partitioning and protocol ownership

Status: [x]
Issue: #15 closed
Depends on: Task 16 complete
Commits: structural checkpoint from `646e02620f3f0dddb1b7e94913567e1edd168a10` through `0a35d951b756e1f311fb5da236d04a2409ba8269`; inventory `6ea901c9a71da0e9d4530b5e72e2bde70a8e6b3d`; guardrails `f5f574a3d9256b41c13fce1ff95ae2494f0da320`, `8eae32ff04967b9ae0cacc70f7232c8d2aafacd8`; isolated declaration fix `9168f681f321c6e8406f361d0524b4df7dfaf977`
Validation: combined Tasks 17–20 gate passed with 45/45 CodepotX tests, strict source/test typechecks, declaration build, architecture checks, baseline artifacts, Publint, and ESM package-resolution checks.

## Goal

Replace the broad contract type warehouse with focused protocol, artifact, operation, port, diagnostic, event, and source modules while preserving every public contract export and serialized field meaning.

## Completed structure

```text
src/contract/
├── protocol/
├── artifacts/{authoring,templating,generation}/
├── operations/{authoring,templating,generation,runtime}/
├── ports/{engines,infrastructure}/
├── diagnostics/
├── events/
├── sources/
└── index.ts
```

## Completion evidence

- [x] Every exported contract symbol and import path is inventoried in `agents/audits/CODEPOTX_CONTRACT_INVENTORY.md`.
- [x] Protocol versions and artifact headers have explicit ownership.
- [x] Artifacts, operations, ports, diagnostics, events, and sources are partitioned by responsibility.
- [x] Legacy flat files remain compatibility shims where supported imports require them.
- [x] Contract internals use focused type-only imports and contain no Node or implementation dependencies.
- [x] Runtime request/result mapping, discriminated unions, readonly fields, and exhaustive artifact kinds remain strict.
- [x] Artifact snapshots remain deterministic, JSON-safe, and baseline-equivalent.
- [x] Declaration output and every published subpath resolve correctly.
- [x] Contract circular-import and forbidden-dependency guardrails pass.
- [x] Central package producer metadata is used by every persisted artifact assembler without changing serialized values.

## Validation

```bash
pnpm --filter codepotx check
pnpm --filter codepotx-cli check
```
