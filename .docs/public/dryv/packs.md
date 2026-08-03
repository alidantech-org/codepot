---
title: Packs and templating
product: dryv-template-jinja
description: Explicit reusable mappings from Runtime IR to target artifacts.
---

# Packs and templating

A pack defines how canonical meaning becomes generated output.

Packs may produce source code, configuration, documentation, reusable packages, project fragments, or complete projects.

A pack must explain:

- which IR items it uses;
- why a template is selected or skipped;
- which values the template receives;
- which files and folders are produced;
- where output is written;
- how generated artifacts depend on one another;
- which bindings and options are required.

Packs cannot invent semantic objects or rely on hidden conventions. Templates own emitted syntax, while language adapters provide target naming, path, module, keyword, and validation facts.

Trust requires pinned identity and versions, deterministic fixtures, conformance tests, dependency provenance, security review, compatibility information, and reproducible output—not popularity alone.
