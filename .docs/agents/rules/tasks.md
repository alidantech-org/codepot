# Task rules

A task is a bounded implementation contract owned by one package or app.

## Location

Tasks live under their owning item:

```text
.docs/packages/<ecosystem>/<package>/tasks/<task>.md
.docs/apps/<app>/tasks/<task>.md
```

`.docs/TODO.md` may point to the current task, but it never duplicates the task body or keeps completed history.

## Creation gate

Create a task only when:

- the problem and owning item are known;
- unresolved architecture decisions have been settled or explicitly scoped out;
- scope, non-goals, allowed paths, acceptance criteria, and validation are concrete;
- the user has approved the work.

Do not create speculative task ledgers, empty milestones, copied plans, or tasks for frozen components.

Dryv is currently being replanned. No Dryv implementation task is active or authorized until a new concrete plan is approved.

## Execution

Before implementation, read the item documentation and exact task, confirm branch and ownership, inspect current code and tests, and preserve unrelated changes. Implement the smallest coherent change and verify it with the task's evidence.

## Completion

After acceptance:

1. incorporate durable facts into current item documentation;
2. archive the task under the mirrored `.archives/.docs` path;
3. remove its pointer from `.docs/TODO.md`;
4. do not create a replacement task unless more approved work exists.
