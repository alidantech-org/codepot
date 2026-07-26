# Task 28 — CodepotG configuration JSON Schemas

Status: [-]
Branch: `chatgpt/codepotx-restart`

## Goal

Ship clean Draft 2020-12 JSON Schemas for `Codepotg.yaml` and `paths.yaml`, retain their `$schema` links in typed runtime contracts, and keep all documentation and task records under `docs/`.

## Implemented

- [x] Add bundled `codepotg.schema.json`.
- [x] Add bundled `paths.schema.json`.
- [x] Assign stable canonical schema identifiers for later deployment.
- [x] Package both schemas in the wheel.
- [x] Add `codepotg.schemas` access helpers.
- [x] Add typed `CodepotFile.schema_uri`.
- [x] Add typed `PathConfig.schema_uri`.
- [x] Permit `$schema` in strict `paths.yaml` loading without weakening unknown-key validation.
- [x] Add schema-linked examples under `docs/examples/`.
- [x] Add schema and loader parity tests.
- [x] Document editor linking and compatibility under `docs/configuration-schemas.md`.

## Remaining validation

- [ ] Ruff passes.
- [ ] Schema-focused tests pass.
- [ ] Existing CodepotG loader and path graph tests pass.
- [ ] Complete package suite passes.
- [ ] Built wheel contains both JSON Schema files.

## Safety constraints

- `$schema` is authoring metadata only and must not change generation output.
- Existing configurations without `$schema` remain valid.
- Strict `paths.yaml` validation must continue rejecting all unrelated unknown keys.
- Runtime cross-reference and cycle validation remains authoritative.
- New documentation and task files belong under `docs/`, not the package root.
