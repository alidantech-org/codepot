# HELPER-12 — CLI Author and API connections

Status: TODO
Prerequisite: HELPER-11 DONE.

## Goal
Give the CLI two explicit communication boundaries: Author Backend process communication and dryv-api HTTP/WebSocket communication.

## Required structure

```text
connections/
├── api/
│   ├── client.py
│   ├── http.py
│   ├── websocket.py
│   └── events.py
└── author/
    ├── client.py
    ├── process.py
    └── result.py
```

API client responsibilities: create/query/cancel builds, fetch plans/status/bundles, observe build events and receive streamed artifacts using the current dryv-api contracts. Author client responsibilities: invoke configured/default author backend, collect canonical compile result/diagnostics and isolate process failure details.

## Enforcement
Delete `api_stdio.py` and all old JSONL/stdio API-host compatibility. Do not duplicate dryv-api protocol models when canonical contracts can be imported. Do not make the Author backend speak the renderer protocol. Transport code must not write project files or derive GenerationPlan semantics.

## Completion
CLI can communicate cleanly with an already-running API and an Author backend through independent typed boundaries. No tests yet.