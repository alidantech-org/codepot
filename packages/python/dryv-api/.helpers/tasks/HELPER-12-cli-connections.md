# HELPER-12 — CLI Author and API connections

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-11 DONE.

## Implemented boundary
`connections/api/` uses the public dryv-api HTTP and build-event WebSocket routes for create/query/plan/preflight/render/cancel/bundle operations. `connections/author/` invokes the one-shot versioned Author host as a subprocess and keeps process diagnostics separate from Canonical IR content.

## Review hardening
The production review keeps blocking planning/preflight work off the ASGI event loop, validates HTTP request fields strictly, bounds Author subprocess execution, validates the complete Author host envelope instead of coercing malformed values, and requires process exit status to agree with the versioned response.

## Enforcement
The old `api_stdio.py` path is deleted. No Runtime planning, renderer semantics, filesystem writes, or compatibility translation lives in either connection boundary. HTTP/WebSocket and Author subprocess contracts remain independent.

## Completion
The CLI can communicate with an already-running dryv-api and with the default Python Author backend through explicit typed owners. Production source was reviewed; executable test certification remains separate.
