---
title: Usage and CLI
product: dryv-cli
description: Connect authored source or Runtime IR with packs, bindings, and output destinations.
---

# Usage and CLI

Usage is the simplest tier.

A project selects:

- authored source or serialized Runtime IR;
- active packs;
- pack options;
- project-specific bindings;
- output destinations;
- generation commands.

The runtime resolves and validates these inputs, creates an inspectable plan, and performs ownership-safe writes only after planning succeeds.

The CLI presents runtime operations. It does not duplicate semantic, planning, plugin, or generation behavior.

A safe workflow is:

```text
validate → inspect → plan → review impact → generate → verify
```

Generation should report selected and skipped templates, provided values, dependencies, output paths, ownership decisions, diagnostics, and trace links.
