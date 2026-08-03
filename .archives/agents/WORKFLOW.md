# Codepot work workflow

## Task lifecycle

1. Read `AGENTS.md`, the project guides, and the active task file.
2. Confirm all dependency tasks are complete.
3. Open or select a GitHub issue for one independently verifiable task.
4. Add the issue number to the task file and mark the task `[~]` in progress.
5. Inspect the relevant old TypeScript and Python behavior before designing replacements.
6. Define or update contracts, types, interfaces, ports, requests, results, and acceptance criteria before implementation.
7. Implement through dependency injection and the approved dependency direction.
8. Validate with the task-specific commands and compatibility fixtures.
9. Commit the completed unit with an issue reference.
10. Add validation evidence and commit SHA to the task file.
11. Mark the task `[x]` only after every acceptance criterion passes.
12. Close the GitHub issue immediately after the task is complete. Never leave a completed task's issue open.

## Issue rules

- One issue should describe one independently reviewable outcome.
- An issue can contain related subtasks when they cannot be validated independently.
- Future issues are created when the work is ready to start, not as a large stale backlog.
- Every issue must identify phase, scope, acceptance criteria, validation, and closure conditions.
- Blocked work remains open and is marked `[!]`; completed work cannot remain open.
- If a task is abandoned, close its issue with the appropriate reason and record the decision in the task file.

## Task status symbols

- `[ ]` planned and not started
- `[~]` in progress with an open issue
- `[!]` blocked with the reason recorded
- `[x]` completed, validated, committed, and issue closed

## Commit rules

- Commit after each important completed unit: contract group, platform adapter, compiler pass, template subsystem, generation subsystem, or major fix.
- Do not mix unrelated phases in one commit.
- Reference the issue in the commit message or body where possible.
- Do not close an issue before the commit is on the working branch and validation evidence is recorded.

## Validation evidence

Every completed task records:

- commands executed;
- test or fixture names;
- expected/actual compatibility comparison;
- package/type validation where relevant;
- commit SHA;
- closed issue number.

When a command cannot run in the available environment, record exactly what was verified and what remains unverified. Do not claim success without evidence.

## Phase gates

- Runtime/platform implementation cannot begin until the shared contract is accepted.
- Authoring implementation cannot begin until the required engine and platform ports exist.
- Templating cannot depend on authoring implementation objects; it begins against stable artifact fixtures.
- Generation cannot begin until authoring and templating ports and artifacts are usable.
- CLI begins only after runtime requests, results, events, and at least one complete generation path are stable.
