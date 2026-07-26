# CodepotG v2 master implementation plan

## 00 — Documentation and boundaries

- [x] Register the agreed clean-room architecture.
- [x] Define the two-file project and pack configuration model.
- [x] Define per-template language ownership, static files, authored barrels, bindings, commands, Git packs, and Python-first interfaces.
- [x] Scaffold implementation and test boundaries with empty tracked directories.
- [ ] Add architecture decision record template and change policy.

## 01 — Package foundation

- [ ] Add `pyproject.toml`, distribution metadata, supported Python versions, typing marker, and development dependencies.
- [ ] Establish the supported `codepotg` public namespace without importing legacy internals.
- [ ] Add import, packaging, and dependency-boundary architecture tests.
- [ ] Add typed diagnostic, source span, result, event, cancellation, and version primitives.

## 02 — Public application API

- [ ] Implement immutable runtime composition and isolated generation sessions.
- [ ] Implement sync and async configure, validate, inspect, migrate, and generate operations.
- [ ] Add in-memory source and artifact APIs.
- [ ] Prohibit printing, `sys.exit`, current-directory mutation, and CLI dependencies below the CLI layer.

## 03 — Configuration registry

- [ ] Implement location-aware YAML and JSON document nodes.
- [ ] Implement `(kind, apiVersion)` typed decoder registry.
- [ ] Implement canonical typed models, semantic validators, migrations, serialization, and schema introspection.
- [ ] Reject unknown fields and generic recursive dictionary merging.

## 04 — Project configuration

- [ ] Implement sources, toolchains, security, global commands, pack instances, outputs, clean scopes, options, bindings, and overrides.
- [ ] Implement project command trust and host policy precedence.
- [ ] Implement legacy `tasks` decoder and explicit migration command.

## 05 — Pack manifest

- [ ] Implement `CodepotgPack.yaml` metadata, content roots, ignore rules, file patterns, selections, files, bindings, rules, dependencies, setup, commands, and lifecycle policy.
- [ ] Implement legacy `paths.yaml` decoder for folders, selections, emissions, barrels, imports, and write policy.
- [ ] Implement pack traits, ownership, requirements, contributions, and setup contracts.

## 06 — File discovery and templates

- [ ] Infer template engines and target syntaxes from filenames using longest-known suffix matching.
- [ ] Classify templates, barrels, static files, partials, and documentation exactly once.
- [ ] Copy static text and binary files by default and implement Gitignore-compatible exclusions.
- [ ] Implement once, each, grouped, aggregate, folder-pattern, and multiple-declared-output planning.
- [ ] Implement authored barrel templates and compatibility barrel templates for legacy packs.

## 07 — Bindings, rules, and imports

- [ ] Implement typed binding catalog and per-template binding usage.
- [ ] Implement module, project-path, package, namespace, raw, barrel, default-barrel, and binding-group imports.
- [ ] Implement unresolved binding policies and strict-mode readiness gates.
- [ ] Implement core-owned rule descriptors, typed patches, merge policies, adapter restrictions, and pack override policy.

## 08 — Plugin system

- [ ] Implement source, language, template-engine, pack-provider, writer, cache, command, and event ports.
- [ ] Implement Python entry-point discovery and instance registries.
- [ ] Validate IDs, aliases, API and IR versions, capabilities, and conflicts.
- [ ] Publish reusable conformance suites.

## 09 — Planning, execution, and safety

- [ ] Implement neutral IR and provenance.
- [ ] Implement template, provider, artifact, import, output, and command graphs with cycle detection.
- [ ] Implement complete pre-render validation and structured readiness statuses.
- [ ] Implement transactional filesystem, memory, and archive writers.
- [ ] Implement ownership manifests, exact comparison, rollback, dry-run, and content-addressed cache.

## 10 — Initial adapters

- [ ] Complete OpenAPI source adapter tasks.
- [ ] Complete TypeScript language adapter tasks.
- [ ] Complete Dart language adapter tasks.
- [ ] Complete sandboxed Jinja engine adapter tasks.

## 11 — Initial packs

- [ ] Migrate and validate the TypeScript SDK pack.
- [ ] Migrate and validate the Dart SDK pack.
- [ ] Migrate and validate the Flutter SDK pack.
- [ ] Prove heterogeneous templates, static files, authored barrels, bindings, setup, commands, and dependency contributions.

## 12 — Configure, CLI, Git, and deployment

- [ ] Implement `codepotg configure`, `pack add`, `configure --check`, and setup reports.
- [ ] Implement typed ecosystem actions and approval records.
- [ ] Implement local, Git, GitHub shorthand, private repository, cache, and lock-file pack resolution.
- [ ] Implement the thin CLI over the Python API.
- [ ] Publish MCP-ready structured operations and server-safe defaults.

## 13 — Compatibility and release

- [ ] Build legacy and canonical configuration fixture matrices.
- [ ] Compare real NestJS, Next.js, Dart, Flutter, documentation, and static-project outputs side by side.
- [ ] Classify intentional differences and eliminate accidental differences.
- [ ] Define the minimal core and batteries-included distribution cutover.
- [ ] Document deprecation windows and complete the release checklist.
