# 02 — Typed configuration and pack contracts

CodepotG v2 has two primary authored configuration files:

- `codepotg.yaml` — everything owned by the user project;
- `CodepotgPack.yaml` — everything owned by one template pack.

V2 does not decode old `tasks`, project-level `language`, `templateDir`, or `paths.yaml`.

## Documents

- [`01-project-config-specification.md`](01-project-config-specification.md) — complete `codepotg.yaml` schema, pack instances, commands, bindings, overrides, outputs, and configure ownership.
- [`02-pack-manifest-specification.md`](02-pack-manifest-specification.md) — complete `CodepotgPack.yaml` schema, heterogeneous files, selections, patterns, bindings, dependencies, setup, commands, and authored barrels.
- [`03-typed-configuration-registry.md`](03-typed-configuration-registry.md) — location-aware documents, exact schema registry, plugin-owned typed sections, introspection, validation, and serialization.
- [`04-rules-overrides-and-bindings.md`](04-rules-overrides-and-bindings.md) — core-owned merge protocol, restrictions, binding kinds, barrels, project paths, and unresolved behavior.
- [`05-commands-security-and-setup.md`](05-commands-security-and-setup.md) — ownership, typed actions, raw commands, trust, capabilities, approvals, environment, phases, and setup questions.
- [`06-toolchains-dependencies-and-manifests.md`](06-toolchains-dependencies-and-manifests.md) — package managers, project units, ecosystem adapters, owned/contributed manifests, dependencies, and install policy.

## Ownership summary

### Project

The project owns sources/spec paths, toolchains, security request, global commands, pack instances, output roots, clean scopes, options, bindings, overrides, and project-owned per-pack commands.

### Pack

The pack owns content discovery, file roles, selections, output expressions, templates, static files, partials, authored barrels, public bindings, language/engine rules, dependencies, setup, manual instructions, and pack-owned commands.

### Template

Every template owns its target syntax, normally inferred from `file-name.<target>.<engine>`. A pack and project can contain many targets.

## Typed processing rule

Raw YAML ends at the configuration infrastructure. Application and domain services receive immutable typed models. Unknown fields are errors, and rule/override merging never uses generic recursive dictionary merging.
