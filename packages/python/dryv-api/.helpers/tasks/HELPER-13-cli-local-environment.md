# HELPER-13 — CLI temporary local environment

Status: TODO
Prerequisite: HELPER-12 DONE.

## Goal
Hide local deployment/process plumbing so a normal install works through one `dryv` command.

## Required structure
Implement `local/environment.py`, `api.py`, `renderer.py`, `process.py`, and `ports.py`.

Required capabilities:
- allocate loopback-only ephemeral ports safely;
- start a temporary local dryv-api when no external API is configured;
- wait for deterministic readiness/fail with child diagnostics;
- start required local renderer helpers, including Jinja, after plan requirements are known where practical;
- track child ownership so externally configured services are never killed;
- propagate cancellation/interrupts;
- always clean owned children on success, error and user cancellation.

## Enforcement
This layer hides topology only; it does not hide semantic decisions. No Runtime construction inside CLI when dryv-api is the selected host path. No hard-coded fixed ports, orphan child processes, shell-string command assembly, or platform-specific path assumptions without a dedicated owner.

## Completion
`LocalEnvironment` can provide API + renderer availability for one command invocation while remaining replaceable by a configured remote API. No tests yet.