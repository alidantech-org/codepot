# Task 00 — Establish Dryv runtime feature boundaries

Status: [ ]
Owner: `packages/python/dryv`
Depends on: approved Dryv client/server architecture and current brainstorm decisions
Validation: architecture tests and documentation checks

## Goal

Refactor `dryv` around independently maintainable Features coordinated by Runtime. Runtime is the composition root; Features own bounded capabilities and expose small public facades. No Feature may become a second runtime or coordinate the whole build.

The target shape is:

```text
dryv/
├── ir/                 # canonical semantic authority
├── features/
│   ├── serialization/
│   ├── project/
│   ├── resources/
│   ├── hashing/
│   ├── ir/
│   ├── packs/
│   ├── planning/
│   ├── cache/
│   ├── authoring/
│   ├── templating/
│   ├── scheduling/
│   ├── artifacts/
│   └── diagnostics/
└── runtime/
    ├── composition.py
    ├── runtime.py
    └── contracts.py
```

This structure borrows the proven DevAuto rule: real capabilities live in named Features, consumers use the Feature public surface, and Runtime coordinates them.

## Required boundaries

- `dryv.ir` owns canonical software meaning and imports no Runtime or Feature implementation.
- `dryv.features.*` must not import `dryv.runtime`.
- Features must not import sibling Feature internals. Any approved cross-feature use must go through the sibling public root and be recorded explicitly in architecture tests.
- Runtime may import Feature public roots and compose them.
- `dryv` must not host HTTP or WebSocket servers.
- `dryv` must not depend on frontend packages such as CLI, VS Code, web, or playground.
- `dryv` must not execute a template engine internally. Templating communicates through established render sessions.
- `dryv` must not execute an author implementation internally. Authoring communicates through canonical IR or established author sessions.
- `dryv` must not mutate the user's project filesystem. It produces artifact/write instructions for a Project Client.
- Do not create vague capability buckets such as `common`, `utils`, `helpers`, `misc`, or `shared`.

## Feature shape

Every top-level Feature must provide one public facade from its package root. Internal files may be organized by the concrete capability, but production code outside the Feature must not import private Feature paths.

A Feature facade must not directly contain low-level effect implementation. It composes the Feature's own contracts/mechanics and exposes capability methods to Runtime.

## Architecture tests

Add tests under `packages/python/dryv/tests/architecture/` that enforce at minimum:

- only the approved top-level Feature directories exist;
- Features do not import Runtime;
- IR does not import Runtime or Features;
- production consumers use Feature public roots;
- sibling Feature imports are denied unless explicitly approved;
- vague feature directory names are rejected;
- Runtime is the only owner allowed to coordinate multiple Features;
- project write operations are absent from `dryv` after the later migration task completes;
- server-hosting dependencies are not introduced into `dryv`.

During migration, tests may temporarily allow explicitly listed legacy modules. Every temporary exception must name the later task that removes it; no wildcard exemptions.

## Non-goals

- Do not move every current file in this task.
- Do not redesign Canonical IR here.
- Do not implement networking here.
- Do not build renderer or author clients here.
- Do not change pack vocabulary that remains under review.

## Allowed paths

- `packages/python/dryv/src/dryv/**` only as needed to establish facades/skeletons without semantic rewrites
- `packages/python/dryv/tests/architecture/**`
- `.docs/packages/python/dryv/**`
- `.docs/TODO.md`

## Acceptance criteria

- The approved Feature catalog is represented in source and enforced by tests.
- Runtime/Feature/IR dependency direction is executable policy, not documentation only.
- No new generation semantics are introduced.
- Temporary legacy exemptions are narrow and point to numbered follow-up tasks.
- Canonical Dryv documentation describes Runtime as coordinator of independent Features.

## Validation

Run the Dryv test suite plus the new architecture tests and `git diff --check`. Record exact passing commands and any temporary architecture exemptions in the task completion evidence.
