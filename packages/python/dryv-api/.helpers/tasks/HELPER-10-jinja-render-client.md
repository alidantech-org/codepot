# HELPER-10 — Rewrite dryv-template-jinja

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-09 DONE AND Author production-code review completed.

## Goal
Replace the old session/stdio renderer with the smallest correct implementation of the renderer-neutral `dryv-api` protocol.

## Required structure

```text
dryv_template_jinja/
├── __init__.py
├── __main__.py
├── py.typed
├── renderer/
│   ├── __init__.py
│   ├── environment.py
│   ├── validation.py
│   ├── rendering.py
│   └── fingerprint.py
└── client/
    ├── __init__.py
    └── connection.py
```

## Responsibilities
- `environment.py`: secure deterministic Jinja environment using `SandboxedEnvironment` and `StrictUndefined`.
- `validation.py`: template syntax/context-contract preflight with renderer diagnostics.
- `rendering.py`: template + context → artifact bytes/chunks with cancellation checkpoints.
- `fingerprint.py`: deterministic fingerprint covering Jinja version and output-affecting semantic configuration/helpers.
- `connection.py`: connect/register with dryv-api, handle validate/render/cancel protocol messages and stream artifact results.

## Enforcement
Import/implement the protocol owned by dryv-api; never duplicate protocol dataclasses or invent Jinja-specific server semantics. No Canonical IR parsing, dryv.yaml handling, pack interpretation, template selection, output-path decisions, local filesystem writes, stdio compatibility, or `JinjaRenderSession` aliases.

## Completion
The persistent Jinja client registers capability/capacity/fingerprint, preflights templates, renders assigned jobs incrementally, streams results and honors cancellation while the receive loop remains active. Production review confirmed the renderer remains semantically naive. No tests were added or run.
