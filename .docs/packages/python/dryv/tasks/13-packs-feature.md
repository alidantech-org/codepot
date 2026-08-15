# Task 13 — Build the Packs Feature for `dryv.pack.yaml`

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Tasks 09, 10 and 12
Validation: pack-manifest tests, resource-reference tests, architecture tests

## Goal

Create `features/packs` as the sole Dryv Engine owner of `dryv.pack.yaml` meaning. Packs define how canonical IR meaning becomes planned generated artifacts, but they do not execute template engines or mutate project files.

## Pack responsibilities

A pack must be able to declare, using only approved vocabulary:

- pack identity/version;
- required Dryv/protocol versions;
- templates and template resource IDs;
- renderer capability required by each template;
- which canonical IR concepts each template consumes/selects;
- invocation/cardinality/grouping behavior once approved;
- explicit context requirements;
- conditions/skip rules once approved;
- planned artifact/output declarations;
- artifact/symbol relationships once approved;
- pack options and required project bindings;
- dependencies on other packs/resources where supported.

All target syntax remains inside template resources. Pack metadata remains language/runtime neutral.

## Vocabulary gate

The brainstorm explicitly leaves selection target naming, invocation vocabulary, filtering, grouping, template variable names, generated symbol vocabulary, imports/exports and barrels under review. This task must not silently choose those names.

Implementation should:

1. inventory current supported pack fields;
2. preserve approved behavior;
3. model unresolved areas behind typed internal contracts only after user-facing vocabulary is approved;
4. reject unknown/unapproved fields rather than accepting arbitrary metadata bags.

## Resource boundary

Pack manifests/templates arrive as Resources. Packs Feature validates logical resource relationships and never directly clones repositories or reads arbitrary host paths.

## Explainability

Every normalized pack declaration must retain enough provenance to explain:

- which declaration selected an item;
- why an invocation exists or is skipped;
- which template resource it uses;
- what context it requested;
- what artifact declaration it caused.

## Non-goals

- Do not render templates.
- Do not finalize unresolved pack vocabulary.
- Do not resolve final artifact dependencies/symbols; Planning owns that.
- Do not access the user filesystem or Git credentials.

## Allowed paths

- `packages/python/dryv/src/dryv/features/packs/**`
- existing generation manifest/discovery models being migrated where owned by pack meaning
- corresponding tests/docs

## Acceptance criteria

- `dryv.pack.yaml` is normalized through one Feature.
- unknown/unapproved metadata cannot silently change behavior.
- template resources and required renderer capabilities are explicit.
- pack options/bindings are typed and deterministic.
- provenance for later explainability is preserved.

## Validation

Test valid/minimal packs, multiple templates, missing resources, renderer capability declarations, options/bindings, version errors, unknown fields and deterministic normalization. Run architecture tests and `git diff --check`.
