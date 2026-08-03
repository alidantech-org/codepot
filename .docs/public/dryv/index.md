---
title: Dryv
product: dryv
description: The active semantic derivation runtime and package family.
---

# Dryv

Dryv is the active Codepot implementation.

It provides a canonical semantic contract between authoring systems and reusable generation packs. Authoring frontends may be implemented in Python, TypeScript, Rust, Codepot language, or another language, but equivalent input must compile into the same Runtime IR.

## Package family

- `dryv` — canonical runtime and IR authority.
- `dryv-author` — Python authoring frontend.
- `dryv-cli` — terminal frontend.
- `dryv-template-jinja` — Jinja adapter.
- `dryv-language-typescript` — TypeScript target adapter.
- `dryv-language-dart` — Dart target adapter.

## Read next

- [Authoring](/docs/dryv/authoring)
- [Runtime IR](/docs/dryv/runtime-ir)
- [Packs and templating](/docs/dryv/packs)
- [Usage and CLI](/docs/dryv/usage)
