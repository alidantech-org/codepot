# Repository structure

```text
apps/          executable applications
packages/      reusable packages grouped by ecosystem
.docs/         all canonical authored documentation
.archives/     historical, read-only implementations and records
README.md      human project entry point
AGENTS.md      AI navigation and safety gate
```

## Applications and packages

Applications and packages may contain source, tests, fixtures, templates, manifests, configuration, generated artifacts where required, licenses, and one concise root `README.md`.

They must not maintain independent architecture folders, task ledgers, plans, audits, contribution rules, deployment guides, or agent instructions. Those belong under `.docs`.

Templates such as `README.md.j2`, test-fixture READMEs, schema descriptions consumed at runtime, and generated documentation artifacts are implementation assets rather than competing project documentation and may remain with their code when required.

## Root cleanliness

Do not add miscellaneous plans, reports, scripts, schemas, notes, or temporary files at the repository root. Place each artifact with its owning application/package or in its canonical `.docs` section.
