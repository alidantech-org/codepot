# Task 22 — Prove the full architecture with a reference pack

Status: [x]
Owner: `packages/python/dryv`
Depends on: Dryv Task 20, `dryv-api` build/render connections, one working Render Client, one Project Client apply path
Validation: full process integration test and trace assertions

> The end-to-end proof is implemented on `develop`. Executable/process certification is still pending because the connected repository environment exposes no checkout/test runner. See [`../PROGRESS-18-25.md`](../PROGRESS-18-25.md).

## Goal

Build the smallest reference scenario that proves the complete architecture from Canonical IR through remote-capable rendering to safe project-side application.

## Reference semantic input

Use canonical meaning equivalent to:

```text
Contract
└── Group Users
    ├── Schema BaseRecord
    │   └── id
    ├── Schema User extends BaseRecord
    │   ├── name
    │   └── email
    └── StorageMapping UserStorage maps User
```

This deliberately proves the approved single-base Schema extension and independent StorageMapping relationship.

## Reference pack

Create a test/reference pack with two templates:

```text
schema-type template
storage-entity template
```

The first emits a TypeScript schema representation such as an interface/type artifact for `User`.

The second consumes the planned schema representation and emits an entity artifact whose template syntax can produce a relationship equivalent to:

```ts
export class UserEntity implements User {
    ...
}
```

The generated `implements` relationship is pack/template behavior. Canonical IR remains Schema + StorageMapping.

## What the test must prove

```text
serialized Canonical IR
→ Serialization
→ IR validation/indexing
→ Schema extension resolution
→ pack loading
→ selection/template invocation
→ canonical JSON context
→ virtual artifact/dependency planning
→ hash/cache identity
→ RenderSession request
→ RenderResult
→ Artifact/WriteInstruction stream
→ API transport
→ Project Client atomic apply
```

## Explainability assertions

The test must be able to inspect/verify why the entity exists:

```text
UserStorage maps User
→ pack declaration selected it
→ entity invocation requires User schema representation
→ planned dependency resolves to type artifact
→ render client receives exact template/context
→ artifact path/content produced
→ Project Client applied it
```

Also verify inherited field provenance: `id` originates from `BaseRecord`; `name/email` originate from `User`.

## Non-goals

- Do not build a full framework project.
- Do not add production template-pack marketplace logic.
- Do not add framework-specific IR concepts.

## Allowed paths

- `packages/python/dryv/tests/**`
- reference/test fixtures under approved Dryv example/fixture paths
- `.docs/packages/python/dryv/**`
- minimal shared integration fixtures in the relevant API/client packages where necessary

## Acceptance criteria

- one real external Render Client renders the reference pack.
- engine never writes the project output directly.
- Project Client applies the streamed instructions safely.
- resulting TypeScript files are deterministic and compile/type-check in the fixture where tooling is available.
- full trace links canonical semantics to generated artifacts.

## Validation

Run the complete integration fixture twice to prove deterministic output/unchanged classification, run target TypeScript validation for generated files, assert trace/provenance, run package architecture tests and `git diff --check`.
