# 02 — Typed project and pack configuration

CodepotG v2 has two authored YAML contracts:

- `codepotg.yaml` — project-owned sources, executables, commands, and pack instances;
- `CodepotgPack.yaml` — pack identity, options, bindings, selections, dependencies between generated emissions, and pack commands.

V2 does not decode old `tasks`, project-level `language`, `templateDir`, or `paths.yaml`.

## Documents

- [`01-project-config-specification.md`](01-project-config-specification.md) — direct local/Git pack sources, semantic inputs, output roots, executables, bindings, and commands.
- [`02-pack-manifest-specification.md`](02-pack-manifest-specification.md) — filesystem discovery, compact selection registry, imports, exports, symbols, bindings, and exact pack commands.
- [`03-typed-configuration-registry.md`](03-typed-configuration-registry.md) — location-aware documents, schema families, introspection, validation, and serialization.
- [`04-rules-overrides-and-bindings.md`](04-rules-overrides-and-bindings.md) — typed project values, restrictions, external bindings, and generated dependency planning.
- [`05-commands-security-and-setup.md`](05-commands-security-and-setup.md) — command trust, exact argument boundaries, approvals, environment, and lifecycle phases.
- [`06-toolchains-dependencies-and-manifests.md`](06-toolchains-dependencies-and-manifests.md) — adapter-owned project/tool integration where real ecosystems require it.
- [`07-complete-project-and-pack-example.md`](07-complete-project-and-pack-example.md) — one linked project using local, Git-monorepo, and independent Git packs plus a generated lock.
- [`../examples`](../examples/README.md) — standalone YAML examples used by documentation and future conformance tests.

## Ownership summary

### Project

The project owns semantic inputs, direct pack sources, executable names/paths, command policy, global commands, pack-instance output roots, options, bindings, and project-owned overrides.

### Pack

The pack owns identity, compatibility, include/exclude rules, public options/bindings, registered selection folders, pack-relative paths, generated imports/exports/symbols, executable defaults, and exact pack commands.

### Filesystem

The `templates/` tree owns literal files, literal directories, dynamic filenames, static assets, partials, and authored barrels. Ordinary files are discovered rather than registered individually.

### Adapters

Language adapters own target import/export syntax and module paths. Template-engine adapters render already planned content. Neither chooses output directories.

## Typed processing rule

Raw YAML ends inside configuration infrastructure. Domain/application services receive immutable typed models. Unknown fields are errors, and no generic recursive dictionary merge is permitted.
