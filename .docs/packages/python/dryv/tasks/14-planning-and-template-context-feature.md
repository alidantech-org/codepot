# Task 14 — Build Planning and canonical template-context generation

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Tasks 12 and 13
Validation: deterministic planning tests, context-contract tests, trace tests

## Goal

Create `features/planning` as the Dryv capability that turns validated IR + normalized packs + project bindings into a deterministic generation plan before rendering starts.

Planning owns generation intelligence. Render Clients receive already-prepared context and must not understand Dryv semantics.

## Planning responsibilities

Planning must produce explicit records for:

- selected semantic items;
- template invocations;
- skipped invocations with reasons;
- canonical JSON template context;
- virtual artifact/output identities and project-relative paths;
- artifact dependencies;
- generated symbol relationships once their vocabulary is approved;
- required renderer capability;
- pack options/project bindings used;
- semantic dependency set used to build the context;
- complete trace/provenance back to IR and pack declarations.

## Context contract

Every invocation receives bounded, serializable JSON-compatible context. Context may contain:

```text
selected semantic subject(s)
owner/group/contract facts where approved
relevant direct fields/capabilities
explicitly requested related semantic facts
derived indexes supplied by IR Feature
resolved project bindings/options
planned artifact/dependency facts
trace metadata
```

Do not pass Python objects, callbacks, lazy Python resolvers or entire unbounded Contracts to Render Clients.

Related semantic data must be projected deliberately. The context builder must record exactly which IR records/branches it consumed so Hashing/Cache can invalidate only affected outputs.

## Virtual output registry

Plan paths/artifact identities before files exist. Other invocations may depend on planned artifacts without waiting for physical writes.

The registry must be deterministic and able to answer:

- which invocation plans an artifact;
- where it will be applied relative to the project/output root;
- which semantic concept(s) caused it;
- which dependencies/symbols it provides or consumes once approved;
- current planning/render status.

## Pack vocabulary caution

Selection keywords, variable names, symbol/provider vocabulary, imports/exports and barrel syntax remain governed by explicit approvals. Planning may have typed internal concepts, but this task must not silently finalize user-facing names.

## Non-goals

- Do not call Render Clients.
- Do not write files.
- Do not persist cache entries.
- Do not embed target-language import syntax.

## Allowed paths

- `packages/python/dryv/src/dryv/features/planning/**`
- current generation planner/context/inspection modules being migrated
- corresponding tests/docs

## Acceptance criteria

- identical IR + packs + bindings produce byte-equivalent normalized plans/context.
- context is plain canonical JSON data and bounded to declared needs.
- planned artifacts exist before rendering and can participate in dependencies.
- every selection/context/artifact decision has an explanation trace.
- planning records semantic dependencies used for incremental invalidation.

## Validation

Test deterministic plans, one semantic item driving multiple invocations, skipped selections, related-context projection, virtual paths, dependency ordering, context serialization and trace explanations. Run architecture tests and `git diff --check`.
