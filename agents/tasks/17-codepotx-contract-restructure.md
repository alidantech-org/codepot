# Task 17 — Contract partitioning and protocol ownership

Status: [~]
Issue: #15 open
Depends on: Task 16 complete
Commit: pending
Validation: inventory and implementation pending

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

- [ ] Inventory every exported contract symbol and current import path.
- [ ] Move protocol versions and artifact header contracts into `protocol/`.
- [ ] Group authoring, template, generation-plan, rendered-generation, manifest, and result artifacts by owner.
- [ ] Split request/result mappings by operation layer.
- [ ] Split infrastructure ports into focused files.
- [ ] Split engine ports into focused files.
- [ ] Move diagnostics, events, and source descriptors into owned folders.
- [ ] Keep compatibility re-exports at `codepotx/contract` during migration.
- [ ] Replace broad internal imports with focused type-only imports where practical.
- [ ] Introduce one package-version source used by artifact producers without creating a protocol change.
- [ ] Remove duplicate shared result or common type definitions only after references are proven equivalent.

## Type-safety requirements

- [ ] Preserve the runtime operation request/result type mapping.
- [ ] Preserve discriminated unions and exhaustive artifact kinds.
- [ ] Preserve readonly and JSON-safe artifact contracts.
- [ ] Do not add circular contract imports.
- [ ] Do not import Zod, Handlebars, YAML, Node APIs, platform implementations, or domain implementations.

## Acceptance criteria

- [ ] Existing root and `codepotx/contract` consumers compile unchanged.
- [ ] Artifact JSON snapshots match the baseline.
- [ ] Declaration output contains no private implementation paths.
- [ ] Architecture checks confirm `contract` depends on no internal Codepot layer.
- [ ] Public export snapshot changes are intentional and reviewed.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```
