---
title: Canonical Runtime IR
product: dryv
description: The only semantic authority shared by every authoring frontend and pack.
---

# Canonical Runtime IR

Runtime IR preserves the software meaning that Dryv explicitly supports.

Every authoring implementation must compile into this same model. Serialized JSON or YAML is a transport representation owned by the runtime, not a competing source of meaning.

The runtime validates identities, references, invariants, versions, and compatibility before planning generation.

## Why it matters

A canonical IR allows:

- several authoring languages to express equivalent software;
- packs to consume one stable vocabulary;
- portable serialized contracts;
- semantic diffs and inspection;
- traceability from authored definitions to generated artifacts;
- future packs to target technologies that did not exist when the contract was authored.

Portability applies only to semantics represented by the IR. Custom algorithms and target-specific behavior remain explicit engineering concerns.
