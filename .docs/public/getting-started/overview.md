---
title: Codepot overview
description: The problem Codepot explores and the role of the active Dryv implementation.
---

# Codepot overview

Modern software relies on mature languages, frameworks, databases, libraries, and runtimes. These systems are valuable, but the same application intent is repeatedly expressed through different decorators, configuration files, schemas, project layouts, APIs, and generated support code.

Codepot explores a semantic layer before those implementation choices.

For example, a required unique customer email, a create operation, an authorization policy, and persistence intent remain meaningful whether the target uses NestJS, FastAPI, PostgreSQL, MongoDB, or a future stack.

Dryv captures supported meaning in a canonical Runtime IR. Packs then decide how that meaning becomes target-specific artifacts.

## Project position

- Dryv is active and under alpha development.
- CodepotG is frozen.
- `codepot-openapi`, `codepotx`, and `codepotx-cli` are frozen.
- The website and documentation application boundary remain active.
- Archived code is historical and read-only.

Codepot does not promise automatic migration of arbitrary handwritten software. It aims to preserve and re-derive the semantics that its canonical model explicitly owns.
