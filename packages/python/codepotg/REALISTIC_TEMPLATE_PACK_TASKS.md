# CodepotG Realistic Template-Pack Tasks

Branch: `chatgpt/codepotx-restart`

Status legend:

```text
[ ] pending
[-] implemented, awaiting local validation
[x] validated from shared command output
```

## Fixture foundation

- [-] Add full generic Nest backend pack derived from the supplied template archive.
- [-] Add full generic Next server-action pack derived from the supplied template archive.
- [-] Add full generic Dart client pack derived from the supplied template archive.
- [-] Remove real company, product, repository, and local-workspace branding.
- [-] Use the large canonical `openapi.json` fixture with fictionalized branding only.
- [-] Add visible `.generated-review/` generation instead of temp-only output.
- [-] Commit representative `AppStatus` generated examples for review.

## Template repairs

- [-] Repair Nest entity barrel collisions by emitting one barrel per resource.
- [-] Repair Nest use-case barrel collisions by emitting one barrel per resource.
- [-] Separate managed `.gen` output from immutable `src/modules` output.
- [-] Add explicit safe write policies to Next and Dart packs.
- [-] Remove Riderescue and Alidantech assumptions from the Dart package template.
- [-] Support both authored and normalized entity relation cardinality names.

## Modern variables

- [-] Expose `normalized`, `domains`, `schema_contract`, `codegen_contract`,
  `entity_contract`, and `frontend_contract` to normal queued legacy generation.
- [-] Use normalized schema IDs in Nest, Next, and Dart schema templates.
- [-] Use normalized codegen resource routes in Nest controllers, Next actions, and Dart
  feature clients.
- [-] Use normalized persistence store and effective-field facts in Nest entities.
- [ ] Migrate each pack from the legacy folder bridge to direct graph selections/emissions.

## Honest verification gate

- [-] Assert the generated sanitized OpenAPI remains larger than 1 MB.
- [-] Assert all planned output paths are unique.
- [-] Assert every planned output is physically written.
- [-] Assert substantial minimum output counts per pack.
- [-] Assert representative AppStatus output and normalized metadata.
- [-] Assert SQLite/JSONL cache and generated output reuse.
- [ ] Run `tests/integration/test_realistic_template_packs.py` locally.
- [ ] Run the complete test suite and Ruff.
- [ ] Record exact output counts, durations, RSS, private bytes, and batch statistics.
- [ ] Promote the realistic pack profiles—not the synthetic debug profile—to release evidence.
