# HELPER-12 — CLI Author and API connections

Status: DONE
Prerequisite: HELPER-11 DONE.

## Implemented boundary
`connections/api/` uses the public dryv-api HTTP and build-event WebSocket routes for create/query/plan/preflight/render/cancel/bundle operations. `connections/author/` invokes the one-shot versioned Author host as a subprocess and keeps process diagnostics separate from Canonical IR content.

## Enforcement
The old `api_stdio.py` path is deleted. No Runtime planning, renderer semantics, filesystem writes, or compatibility translation lives in either connection boundary. HTTP/WebSocket and Author subprocess contracts remain independent.

## Completion
The CLI can communicate with an already-running dryv-api and with the default Python Author backend through explicit typed owners. No tests were added or run.
