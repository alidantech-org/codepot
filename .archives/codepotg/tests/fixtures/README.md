# CodepotG test fixtures

`openapi.json` and `openapi.yaml` are the canonical real-world Codepot contract fixtures.
They are semantically equivalent representations of the same Alidantech API and include:

- OpenAPI 3.1 paths, servers, security, parameters, bodies, and responses;
- schema models, DTOs, enums, primitives, projections, and reusable components;
- `x-codegen` resources, access policies, hooks, cache metadata, entities, relations, constraints, and frontends.

Use these files for contract-preservation, JSON/YAML parity, end-to-end generation,
JSONL, graph-planning, normalized-root, and language-pack integration tests.

Small inline documents are reserved for focused unit tests that intentionally create one
malformed reference, cycle, collision, missing value, or other isolated boundary condition.
They must not replace the canonical fixtures in high-level integration coverage.

Project fixtures under `projects/` remain self-contained packs for testing configuration
discovery and exact project-owned outputs. At least one integration path for each major
runtime feature must also run against the canonical real-world fixtures.
