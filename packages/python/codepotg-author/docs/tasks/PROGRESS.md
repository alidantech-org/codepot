# codepotg-author progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-27 | `e3dc8b32` | Package root | complete | Documentation/files only; runtime tests not applicable. | Added the package README and locked the one-IR, neutral-authoring, canonical-transport product boundary. |
| 2026-07-27 | `877010b6` | Documentation and project scaffold | complete | Documentation review and repository-path verification; runtime implementation and tests have not started. | Added package metadata, approved idea, eight focused design documents, AUTHOR-001..AUTHOR-030 ledger, dependency/parallel rules, full implementation prompt, and mirrored source/test/example/benchmark directories with `.gitkeep` files. |
| 2026-07-27 | `6cea4ad7` | Shared parallel lane | complete | Coordination-document review only. | Registered `codepotg-author` as an independent package lane and recorded that new semantics remain intentional core gates rather than author-private extensions. |
| 2026-07-27 | `7b13c4f2` | Base integration | complete | Scoped merge audit against starting base `b3a36980`; only `packages/python/codepotg-author/**` and the shared parallel registry changed. | Merged the scaffold into `chatgpt/codepotx-restart`; feature documentation branch remains available for audit. |
| 2026-07-27 | `9f12c442` | Python-version audit correction | complete | Documentation review only. | Clarified that generic ref notation is conceptual and Python 3.11 implementation must use `TypeVar`/`Generic`, not Python 3.12-only PEP 695 class syntax. |
| 2026-07-27 | `3e3b3e5d` | Typed semantics, projections, Pydantic v2, and public IR compiler | implementation complete; verification pending | Source-level contract audit against public `codepotg.ir`. | Replaced the dynamic property bridge, added typed operation/event/policy/storage/view/workflow payloads, recursive model discovery, deterministic schema dependency ordering, projection expansion, enum validation, and immutable public IR assembly. |
| 2026-07-27 | `f41f4c82` | Canonical JSON/YAML transport and integration coverage | implementation complete; verification pending | Added strict transport and integration tests; execution pending on the user workstation. | Added tagged canonical transport, strict top-level versions/fields, duplicate-key-safe YAML/JSON loading, core validation after decode, and wheel/build dependencies. |
| 2026-07-27 | `9f74b2c6` | Accuracy hardening | implementation complete; verification pending | Source-level audit of constructor signatures, recursive enums, explicit group ownership, foreign refs, and transport dataclass fields. | Corrected public diagnostic construction, enum reuse, HTTP pair validation, group leakage, ref validation, provenance transport, and init-only dataclass decoding. |

## Open design gates

- Core `TagSet` and safe template tag API.
- Categorized guidance/info contract.
- Typed connected field-capability facets.
- Neutral value-source object and relationships.
- Contract-level presentation, placements, addresses, navigation, selectors, and contexts.
- Expanded HTTP input/output bindings not present in current public facet.
- Final ownership and public location of canonical IR JSON/YAML codec.

These gates are not permission to add author-private semantic objects or hide behavior in `extensions`/`raw`.

## Promotion gate

The feature branch remains `in_progress` until the following are reproduced from the synchronized checkout: author pytest, core pytest, mypy, pyright, package build, wheel-content inspection, isolated wheel installation, JSON/YAML smoke round trips, and a clean scoped diff. Ruff findings may be repaired with `ruff check --fix .` and `ruff format .` before final verification.
