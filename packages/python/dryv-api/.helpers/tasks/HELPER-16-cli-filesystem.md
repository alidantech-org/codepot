# HELPER-16 — CLI filesystem diff, staging and apply

Status: TODO
Prerequisite: HELPER-15 DONE.

## Goal
Create the single safe local filesystem mutation boundary for generated artifacts.

## Required structure
Implement `filesystem/paths.py`, `inspect.py`, `diff.py`, `stage.py`, and `apply.py`.

Required capabilities:
- normalize/validate project-relative artifact destinations and reject traversal, absolute/drive escape and project-root escape;
- inspect current local content/hashes;
- classify CREATE, UPDATE, UNCHANGED and CONFLICT, with managed-delete behavior only when explicitly supported by current contracts;
- build an inspectable change set before mutation;
- stage writes safely and apply atomically as far as the platform permits;
- protect local modifications/ownership according to explicit generated-state metadata rather than blind overwrite;
- surface precise per-file failures and avoid partially claiming success.

## Enforcement
This directory is the only helper owner of generated project-file mutation. API, Runtime, Jinja and artifact transport must never write these files. Do not execute arbitrary lifecycle shell commands here; command execution requires a separately approved contract/owner.

## Completion
Verified artifacts can be previewed/diffed and safely applied to the project with explicit outcomes. No tests yet.