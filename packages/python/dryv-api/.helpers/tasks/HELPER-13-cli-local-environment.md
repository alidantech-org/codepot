# HELPER-13 — CLI temporary local environment

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-12 DONE.

## Implemented topology
`LocalEnvironment` owns only services it starts. The default path reserves a loopback listening socket, starts one local dryv-api ASGI host, and launches required renderer helpers as owned subprocesses after renderer requirements are known. External API URLs remain unowned and are never stopped by the CLI.

Jinja connects through the public renderer WebSocket protocol; the CLI does not register an in-memory renderer shortcut. Child argv is explicit with `shell=False`, readiness is bounded, and owned services are cleaned on normal exit or exceptions.

## Review hardening
The local topology now relies on the same public HTTP/WebSocket contracts as remote deployment. The API no longer blocks its ASGI loop during planning/preflight, Jinja honors its advertised concurrency, and renderer worker/sender failures terminate or report through the protocol rather than silently stalling local generation.

## Completion
One command invocation can acquire a local API and renderer availability without fixed ports or user-visible topology. Production source was reviewed; executable test certification remains separate.
