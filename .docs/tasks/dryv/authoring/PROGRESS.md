# dryv-author progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-27 | `e3dc8b32` | Package root | complete | Documentation/files only; runtime tests not applicable. | Added the package README and locked the one-IR, neutral-authoring, canonical-transport product boundary. |
| 2026-07-27 | `877010b6` | Documentation and project scaffold | complete | Documentation review and repository-path verification; runtime implementation and tests had not started. | Added package metadata, design documents, task ledger, implementation prompt, and mirrored project structure. |
| 2026-07-27 | `6cea4ad7` | Shared parallel lane | complete | Coordination-document review only. | Registered `dryv-author` as an independent package lane. |
| 2026-07-27 | `7b13c4f2` | Base integration | complete | Scoped merge audit. | Merged the scaffold into `chatgpt/codepotx-restart`. |
| 2026-07-27 | `9f12c442` | Python-version audit correction | complete | Documentation review only. | Clarified Python 3.11 generic implementation requirements. |
| 2026-07-27 | `3e3b3e5d` | Typed semantics, projections, Pydantic v2, and public IR compiler | implementation complete; verification pending | Source-level contract audit against public `dryv.ir`. | Added typed operation/event/policy/storage/view/workflow payloads, recursive model discovery, deterministic schema dependency ordering, projection expansion, enum validation, and immutable public IR assembly. |
| 2026-07-27 | `f41f4c82` | Package-local JSON/YAML transport and integration coverage | implemented but superseded for orchestration | Added strict transport and integration tests; execution pending on the user workstation. | The package-local envelope is not the core canonical transport consumed by the built-in `ir` adapter. Use the core codec until `AUTHOR-AUDIT-001` is fixed. |
| 2026-07-27 | `9f74b2c6` | Accuracy hardening | implementation complete; verification pending | Source-level audit of constructor signatures, recursive enums, explicit group ownership, foreign refs, and transport dataclass fields. | Corrected public diagnostic construction, enum reuse, HTTP pair validation, group leakage, ref validation, provenance transport, and init-only dataclass decoding. |
| 2026-07-27 | `b8411b71` | Six-package connectability audit | fix required / review | See `docs/tasks/AUDIT_FIXES.md` and the connected manual workspace under `dryv/examples/manual/connected-project`. | Recorded one canonical-transport owner, synchronized release commands, and evolved-core authoring gaps. |

## Current compiler coverage

Implemented:

- author sessions and typed refs;
- reusable properties and structural object/enum schemas;
- projections and derivations;
- recursive Pydantic v2 compilation;
- groups and explicit ownership;
- operations, events, policies, storage mappings, views, and workflows;
- deterministic public `dryv.ir.Contract` compilation;
- final core validation and public diagnostics.

## Published core contracts not yet fully authored

Core now publishes these contracts; they are author-package implementation work, not blocked core design gates:

- `TagSet`;
- `GuidanceNote` / `GuidanceKind`;
- field capabilities;
- value sources;
- presentations and entries.

Expanded HTTP input/output bindings remain limited by the current public HTTP facet.

## Required transport rule

The orchestration-compatible path is:

```text
Author.compile().contract
    -> dryv.ir.contract_to_json / contract_to_yaml
    -> built-in ir source adapter
```

The duplicate author-package transport must be delegated to core or removed under `AUTHOR-AUDIT-001`.

## Promotion gate

The package remains in review until the following are reproduced from the synchronized checkout:

- author pytest;
- core pytest;
- Ruff and format;
- mypy;
- pyright;
- package build;
- wheel-content inspection;
- isolated core+author wheel installation;
- author compile -> core codec -> built-in `ir` adapter smoke;
- the connected Python-authoring manual route;
- clean scoped diff/status evidence.
