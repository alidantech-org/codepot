# Task rules

A task is a bounded implementation contract owned by one package or app.

## Location

Tasks live under their owning item:

```text
.docs/packages/<ecosystem>/<package>/tasks/<task>.md
.docs/apps/<app>/tasks/<task>.md
```

`.docs/TODO.md` points to current work but does not duplicate task bodies.

## Creation gate

Create a task only when:

- the problem and owning item are known;
- architecture decisions required for the task are approved;
- scope, non-goals, allowed paths, completion evidence and ordering are concrete;
- the user has approved the work.

Do not create speculative task ledgers, empty milestones, copied plans or tasks for frozen components.

## Execution

Before implementation:

1. work only on `develop`;
2. read the package/app canonical documentation and implementation rules;
3. read the exact active task;
4. inspect current production code before editing;
5. preserve unrelated user work;
6. follow the task's explicit approval and validation gates.

Implement the smallest coherent production change that satisfies the task. Do not expand scope to preserve superseded architecture.

## Test/validation gates

A task may explicitly defer test creation until a user approval gate. When it does:

- do not create, modify or rewrite tests;
- do not add compatibility production code merely to satisfy old tests;
- do not create test-only adapters or alternate public contracts;
- treat the approved production architecture as authoritative;
- begin new test work only after the user explicitly lifts the gate.

This rule is currently mandatory for the active Dryv Engine and `dryv-api` refactor.

## Completion

Do not mark a task complete unless its required production structure, ownership boundaries and completion evidence are actually present.

After the user accepts a completed body of work:

1. incorporate durable facts into current package/app documentation;
2. archive superseded/completed task material when appropriate;
3. update `.docs/TODO.md` to the next approved task;
4. do not create new follow-on work without approval.

When documentation, task instructions and implementation disagree, stop and resolve the contradiction instead of guessing.
