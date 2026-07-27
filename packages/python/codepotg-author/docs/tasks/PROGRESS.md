# codepotg-author progress

| Date | Commit | Task | Status | Tests/evidence | Notes |
|---|---|---|---|---|---|
| 2026-07-27 | `e3dc8b32` | Package root | complete | Documentation/files only; runtime tests not applicable. | Added the package README and locked the one-IR, neutral-authoring, canonical-transport product boundary. |
| 2026-07-27 | `877010b6` | Documentation and project scaffold | complete | Documentation review and repository-path verification; runtime implementation and tests have not started. | Added package metadata, approved idea, eight focused design documents, AUTHOR-001..AUTHOR-030 ledger, dependency/parallel rules, full implementation prompt, and mirrored source/test/example/benchmark directories with `.gitkeep` files. |
| 2026-07-27 | `6cea4ad7` | Shared parallel lane | complete | Coordination-document review only. | Registered `codepotg-author` as an independent package lane and recorded that new semantics remain intentional core gates rather than author-private extensions. |
| 2026-07-27 | `7b13c4f2` | Base integration | complete | Scoped merge audit against starting base `b3a36980`; only `packages/python/codepotg-author/**` and the shared parallel registry changed. | Merged the scaffold into `chatgpt/codepotx-restart`; feature documentation branch remains available for audit. |
| 2026-07-27 | `9f12c442` | Python-version audit correction | complete | Documentation review only. | Clarified that generic ref notation is conceptual and Python 3.11 implementation must use `TypeVar`/`Generic`, not Python 3.12-only PEP 695 class syntax. |

## Open design gates

- Core `TagSet` and safe template tag API.
- Categorized guidance/info contract.
- Typed connected field-capability facets.
- Neutral value-source object and relationships.
- Contract-level presentation, placements, addresses, navigation, selectors, and contexts.
- Expanded HTTP input/output bindings not present in current public facet.
- Final ownership and public location of canonical IR JSON/YAML codec.

These gates are not permission to add author-private semantic objects or hide behavior in `extensions`/`raw`.
