# Codepot

Codepot explores deterministic software derivation from a portable, human- and machine-readable description of software intent.

The active implementation is **Dryv**. Dryv separates software meaning from target-specific code generation so the same canonical Runtime IR can be authored through different frontends and consumed by reusable, explicit template packs.

```text
Authoring source
    ↓
Dryv author compiler
    ↓
Canonical Dryv Runtime IR
    ↓
Runtime validation, loading, inspection, and planning
    ↓
Pack selection, binding, and rendering
    ↓
Generated files and existing target runtimes
```

Codepot does not replace programming languages, databases, frameworks, compilers, or application runtimes. It provides a semantic layer above them. See [`.docs/WHY.md`](.docs/WHY.md) for the project thesis and research position.

## Current development status

### Active

- [`apps/docs`](apps/docs/README.md) — dedicated documentation application boundary.
- [`apps/site`](apps/site/README.md) — public website and current documentation renderer.
- [`packages/python/dryv`](packages/python/dryv/README.md) — canonical runtime, Runtime IR, planning, and generation orchestration.
- [`packages/python/dryv-author`](packages/python/dryv-author/README.md) — Python authoring frontend that compiles to Runtime IR.
- [`packages/python/dryv-cli`](packages/python/dryv-cli/README.md) — terminal frontend over the runtime.
- [`packages/python/dryv-template-jinja`](packages/python/dryv-template-jinja/README.md) — Jinja template-engine adapter.
- [`packages/python/dryv-language-typescript`](packages/python/dryv-language-typescript/README.md) — TypeScript target adapter.
- [`packages/python/dryv-language-dart`](packages/python/dryv-language-dart/README.md) — Dart target adapter.

### Frozen

The following packages are retained for existing users and historical comparison but are not active development targets:

- `packages/python/codepotg`
- `packages/nodejs/codepot-openapi`
- `packages/nodejs/codepotx`
- `packages/nodejs/codepotx-cli`

Frozen packages change only through an explicitly approved maintenance task. Everything under `.archives/**` is historical and read-only. The canonical status registry is [`.docs/project/component-status.md`](.docs/project/component-status.md).

## Repository structure

```text
apps/                         executable applications
packages/<ecosystem>/         reusable packages grouped by ecosystem
.docs/                        all canonical authored documentation
.archives/                    historical, read-only material
README.md                     human project entry point
AGENTS.md                     AI contributor router and safety gate
```

Applications and packages keep only a concise local `README.md`. Architecture, plans, tasks, audits, operations, public documentation, and AI guidance are maintained once under [`.docs/`](.docs/README.md).

## Documentation

- [Why Codepot exists](.docs/WHY.md)
- [Documentation index](.docs/README.md)
- [Project and component status](.docs/project/README.md)
- [Approved architecture](.docs/architecture/README.md)
- [Dryv product documentation](.docs/products/dryv/README.md)
- [Application documentation](.docs/apps/README.md)
- [Task system](.docs/tasks/README.md)
- [AI contributor system](.docs/agents/README.md)
- [Public documentation source](.docs/public/README.md)

The existing [`.docs/plan/`](.docs/plan/README.md) and [`.docs/research/`](.docs/research/README.md) collections remain separate preserved bodies of work.

## Development workflow

Repository work is performed directly on the existing `develop` branch. Contributors and AI agents must not create branches unless the repository policy is explicitly changed by the project owner.

Implementation work must be backed by a ready task under [`.docs/tasks/`](.docs/tasks/README.md), follow the approved architecture, remain inside declared paths, and record exact validation evidence.

AI contributors must begin with [`AGENTS.md`](AGENTS.md).

## Maturity

Dryv is under active alpha development. The architecture is intentionally explicit and testable, but broad claims about portability, migration cost, AI efficiency, and reduced duplicated verification remain hypotheses to be demonstrated through complete reference systems and published evidence.

## License

See [`LICENSE`](LICENSE).
