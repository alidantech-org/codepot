# Dryv master implementation plan

Dryv is the reproducible software derivation runtime in the Codepot ecosystem. This plan covers the renamed Python package family and does not preserve compatibility with the archived generator.

## Stage 1 — Rebrand and package integrity

- [x] Rename the runtime distribution and import namespace to `dryv`.
- [x] Rename authoring, Jinja, TypeScript, and Dart packages.
- [x] Rename project files, pack manifests, API versions, entry-point groups, and ownership state paths.
- [x] Remove the retired source package and its active examples.
- [ ] Verify no old names or retired source references remain.
- [ ] Run lint, formatting, tests, builds, and isolated-wheel checks for every renamed package.

Exit gate: all renamed packages install together and the connected manual project passes from editable installs and real wheels.

## Stage 2 — Runtime package boundary

- [ ] Remove command parsing and terminal output from `dryv`.
- [ ] Introduce a public `DryvRuntime` facade.
- [ ] Keep canonical IR, project/pack contracts, planning, rendering coordination, and managed output in `dryv`.
- [ ] Publish stable runtime request/result types for CLI, IDE, server, notebook, and test hosts.
- [ ] Prove `dryv` has no dependency on `dryv-cli` or `dryv-author`.

Exit gate: runtime operations are fully usable without any user-interface package installed.

## Stage 3 — Contract providers

- [ ] Define a public contract-provider protocol.
- [ ] Support canonical IR files.
- [ ] Support a configured Python module and callable.
- [ ] Support host-supplied in-memory contracts.
- [ ] Validate provider results through the canonical Dryv kernel.
- [ ] Report import, callable, type, cancellation, and validation failures safely.

Exit gate: typed Python authoring can feed the runtime without writing JSON or YAML first.

## Stage 4 — Canonical IR and transport

- [x] Closed immutable semantic kernel.
- [x] Stable semantic IDs, names, refs, groups, schemas, operations, policies, events, storage, views, workflows, presentations, tags, and guidance within published behavior versions.
- [x] Cross-reference validation.
- [x] Deterministic JSON/YAML transport and strict decoding.
- [ ] Finalize runtime-only transport ownership and remove duplicate compatibility exports.
- [ ] Publish transport and behavior-version reference documentation.

Exit gate: every supported IR fixture round-trips exactly and produces a stable canonical digest.

## Stage 5 — Typed project and pack configuration

- [x] `dryv.yaml` typed project model.
- [x] `DryvPack.yaml` typed pack model.
- [x] Safe YAML/JSON, duplicate-key rejection, unknown-field rejection, bounded values, and path containment.
- [x] Pack options, bindings, selections, imports, exports, paths, and symbols.
- [ ] Replace the file-only source configuration with contract-provider configuration.
- [ ] Add runtime introspection suitable for validators, CLI help, IDEs, and cookbook tooling.

Exit gate: valid examples decode into immutable models and invalid configuration fails with precise diagnostics.

## Stage 6 — Plugin system

- [x] Public plugin descriptors and conflict validation.
- [x] Python entry-point discovery.
- [x] Source, language, and template-engine protocols.
- [x] Session-owned plugin instances.
- [ ] Add `validate_plugin` and plugin inspection runtime operations.
- [ ] Publish capability and compatibility reference documentation.
- [ ] Expand plugin categories only after real package needs justify them.

Exit gate: third-party plugins install and validate through public contracts without private kernel access.

## Stage 7 — Pack discovery and planning

- [x] Deterministic local pack discovery.
- [x] Ignore rules, partials, static files, binary files, and suffix inference.
- [x] Fixed core-owned selectors and safe path expressions.
- [x] Stable artifact identities and complete collision checks before rendering.
- [x] Generated dependency and module/path fact resolution.
- [ ] Improve provider ambiguity diagnostics.
- [ ] Publish serializable artifact explanations and impact edges.

Exit gate: every planned artifact has a stable cause and no invalid plan reaches rendering or writing.

## Stage 8 — Rendering and target plugins

- [x] Immutable prepared contexts.
- [x] Sandboxed Jinja rendering.
- [x] TypeScript target validation and module-path facts.
- [x] Dart target validation and URI/path facts.
- [x] Static and binary passthrough.
- [ ] Add official pack fixtures beyond the connected manual SDKs.
- [ ] Verify generated projects against real target tools after every contract change.

Exit gate: templates own every emitted character while plugins provide only validated facts.

## Stage 9 — Managed output

- [x] Deterministic memory output.
- [x] Deterministic archive output.
- [x] Transactional managed filesystem output.
- [x] Manual-edit and unmanaged-collision protection.
- [x] Safe deletion of unchanged stale managed files.
- [ ] Add fault injection across every commit phase.
- [ ] Expand Windows file-lock and interrupted-write coverage.

Exit gate: failure before commit leaves the destination and ownership state unchanged.

## Stage 10 — `dryv-cli`

- [ ] Create the standalone `dryv-cli` distribution.
- [ ] Move `plan` and `generate` parsing/output from the runtime package.
- [ ] Add `validate project`, `validate pack`, and `validate plugin`.
- [ ] Add plugin listing and inspection.
- [ ] Add canonical IR emission.
- [ ] Add ownership-state inspection.
- [ ] Keep every command as a thin call to a public runtime operation.

Exit gate: uninstalling `dryv-cli` does not remove any runtime capability.

## Stage 11 — Explain, impact, and incremental generation

- [ ] Complete semantic-to-selection and selection-to-artifact edges.
- [ ] Include generated-provider, template, partial, config, and pack causes.
- [ ] Publish blast-radius results for CLI, IDE, server, and MCP hosts.
- [ ] Implement incremental generation only after equivalence with a complete generation is proven.

Exit gate: incremental output is byte-for-byte equal to a clean full generation.

## Stage 12 — Trust, commands, and remote packs

- [ ] Design exact command plans, provenance, approvals, environment restrictions, timeouts, cancellation, and process cleanup.
- [ ] Keep command arguments opaque; do not infer package-manager syntax.
- [ ] Implement a generic Git provider using existing credentials.
- [ ] Resolve immutable commits and contained snapshots.
- [ ] Implement `dryv.lock.yaml` without credentials or generated output hashes.
- [ ] Support offline integrity verification.

Exit gate: untrusted behavior remains fail-closed and every approved action is tied to exact immutable inputs.

## Stage 13 — Cookbook and ecosystem documentation

- [ ] First project.
- [ ] Typed Python authoring.
- [ ] Canonical IR inspection and transport.
- [ ] Local pack creation.
- [ ] Jinja templates and partials.
- [ ] TypeScript generation.
- [ ] Dart generation.
- [ ] Pack options, bindings, selectors, and dependencies.
- [ ] Plugin development and validation.
- [ ] Managed output safety and reproducible builds.

Exit gate: every recipe is executable against the published packages and has expected output and failure guidance.

## Release gate

- no old package names or retired source references;
- runtime and CLI responsibilities are separated;
- authoring feeds the runtime directly in memory;
- all public APIs are typed and documented;
- lint and formatting pass;
- every package test suite passes;
- wheels and sdists contain only intended files;
- fresh-wheel plugin discovery passes;
- generated TypeScript compiles;
- generated Dart analyzes;
- deterministic and writer-safety scenarios pass;
- final branch and working tree are clean.
