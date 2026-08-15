# Task 01 — Add Node/VS Code project resource and apply utilities

Status: [ ]
Owner: `packages/nodejs/dryv-client`
Depends on: Task 00 and Dryv CLI Project Client/write semantics
Validation: Node workspace tests, path/hash/apply safety tests

## Goal

Add an optional Node-only project capability on top of the transport client so VS Code extensions, desktop apps and other trusted local Node frontends can collect Dryv project resources and safely apply Artifact/WriteInstruction streams using the same rules as the Python CLI.

Browser/web builds continue to use transport/preview/download only unless paired with a trusted local companion.

## Node project resource responsibilities

Support:

- project-root and `dryv.yaml` discovery;
- project-relative resource collection;
- content hashing/resource manifests;
- local pack/template/serialized IR collection;
- private Git pack acquisition through the user's existing Git environment without transmitting credentials;
- previous managed-output manifest loading;
- missing-resource upload through the TypeScript API client.

## Node filesystem apply responsibilities

Support the same safe rules as the Python Project Client:

```text
CREATE
UPDATE with expected previous hash
UNCHANGED verification
DELETE_MANAGED only when previous ownership/hash matches
```

Use atomic writes where platform/runtime permits, reject path traversal, and never silently overwrite user-modified managed files.

Persist the next managed-output manifest only after successful apply.

## VS Code consumption

Design APIs suitable for a VS Code extension to:

- show plan/progress/diagnostics;
- preview generated diffs;
- apply accepted write instructions;
- cancel a build;
- report apply acknowledgements back to `dryv-api`.

Do not put VS Code UI code inside this package.

## Browser boundary

The browser entrypoint/bundle must not import Node filesystem/process modules. Keep Node project utilities behind explicit Node exports/build targets.

## Non-goals

- Do not implement a VS Code extension here.
- Do not replicate Dryv planning/IR logic.
- Do not give browser code arbitrary local filesystem access.

## Allowed paths

- `packages/nodejs/dryv-client/**`
- `.docs/packages/nodejs/dryv-client/**`
- shared project/artifact protocol artifacts

## Acceptance criteria

- Node consumers can collect the same logical resource bundle as the Python CLI for equivalent fixtures.
- managed-output apply semantics match the approved Project Client safety rules.
- browser build remains free of Node filesystem dependencies.
- VS Code/desktop callers can use the package without importing Dryv Engine.

## Validation

Test resource collection/hash equivalence, create/update/unchanged/delete safety, user-edit conflicts, path traversal, managed manifest commit, API acknowledgements and browser bundle separation. Run Node checks and `git diff --check`.
