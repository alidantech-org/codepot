# Codepot and Dryv architecture

The governing model is:

```text
Authoring
    ↓
Canonical Dryv Runtime IR
    ↓
Templating
    ↓
Usage and generated output
```

Ownership remains separate:

```text
Authoring defines software.
Runtime owns canonical meaning.
Packs define code emission.
Usage connects IR, packs, and destinations.
The CLI presents one unified experience.
```

Start with [`governance/00-approved-architecture.md`](governance/00-approved-architecture.md) and [`governance/04-closed-semantic-kernel.md`](governance/04-closed-semantic-kernel.md).

The remaining sections cover foundation, configuration, generation, plugins, distribution, and the clean rewrite. Changes to these contracts require the process in [`governance/02-design-change-policy.md`](governance/02-design-change-policy.md).
