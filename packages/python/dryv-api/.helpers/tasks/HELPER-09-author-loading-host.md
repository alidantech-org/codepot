# HELPER-09 — Author loading and host boundary

Status: TODO
Prerequisite: HELPER-08 DONE.
Review gate: AUTHOR PRODUCTION-CODE REVIEW after completion.

## Goal
Make the Python Author usable by the CLI/process boundary without mixing process transport into semantic authoring.

## Scope
Implement `loading/module.py`, `loading/target.py`, `loading/discovery.py` and `host/contracts.py`, `host/compile.py`, `host/__main__.py`.

Loading resolves an explicit user authoring target/module and obtains the Author entry object/function. Host provides a small process-facing compile/validate contract suitable for CLI invocation and returns canonical diagnostics/IR using the current agreed wire boundary.

## Enforcement
`compiler/` must not start subprocesses, speak HTTP/WS, or own transport serialization mechanics. `host/` is an outer adapter. No server is required for Author merely because dryv-api is networked. No old AuthorSession/stdio API compatibility contract.

## Completion
CLI can invoke the Author backend as an isolated process and receive a versioned canonical IR result/diagnostics without learning Author internals.

## Mandatory stop
After this task, STOP. Do not implement HELPER-10 or any tests until the complete dryv-author production architecture/code is reviewed and explicitly approved.