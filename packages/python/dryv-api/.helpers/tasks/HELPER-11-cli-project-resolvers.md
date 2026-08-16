# HELPER-11 — CLI project model and resolvers

Status: TODO
Prerequisite: HELPER-10 DONE.

## Goal
Rebuild dryv-cli as a modular reference Project Client starting with local project discovery and resource resolution.

## Required owners
Implement `project/` (`discovery.py`, `project.py`, `config.py`, `snapshot.py`) and `resolvers/` (`ir.py`, `author.py`, `packs.py`, `resources.py`, `destination.py`) under the approved CLI architecture.

Required capabilities:
- discover project root and `dryv.yaml` deterministically;
- represent the local project/config without interpreting Runtime semantics;
- resolve whether Canonical IR is supplied directly or must come from an Author backend;
- resolve local pack directories/resources into explicit upload/bundle resources with stable logical paths and hashes;
- resolve output destination boundaries;
- snapshot relevant local generated/project state for later diff/apply.

## Enforcement
CLI resolvers answer **where/how to obtain inputs**, never what pack selectors or IR relationships mean. Do not copy Runtime pack parsing/planning into CLI. Do not write files in resolvers. Do not retain the old monolithic `project_client.py` contract as an adapter.

## Completion
A command can discover and collect all inputs needed to call dryv-api without knowing Runtime internals. No tests yet.