# HELPER-09 — Author loading and host boundary

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-08 DONE.
Review gate: AUTHOR PRODUCTION-CODE REVIEW completed.

## Goal
Make the Python Author usable by the CLI/process boundary without mixing process transport into semantic authoring.

## Scope
Implement `loading/module.py`, `loading/target.py`, `loading/discovery.py` and `host/contracts.py`, `host/compile.py`, `host/__main__.py`.

Loading resolves an explicit user authoring target/module and obtains the Author entry object/function. Host provides a small process-facing compile/validate contract suitable for CLI invocation and returns canonical diagnostics/IR using the current agreed wire boundary.

## Enforcement
`compiler/` must not start subprocesses, speak HTTP/WS, or own transport serialization mechanics. `host/` is an outer adapter. No server is required for Author merely because dryv-api is networked. No old AuthorSession/stdio API compatibility contract.

## Completion
CLI invokes the Author backend as an isolated one-shot process and receives a versioned canonical IR result/diagnostics without learning Author internals. Production review additionally hardened Windows path target parsing and stdout protocol isolation. No tests were added or run.
