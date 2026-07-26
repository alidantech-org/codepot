# Jinja template-engine tasks

## Foundation

- [ ] Add isolated package metadata, entry point, engine suffixes, versions, and capabilities.
- [ ] Add architecture tests proving no source, language, CLI, output-writer, or command ownership.
- [ ] Implement adapter factory and immutable per-runtime configuration.

## Locked configuration contract

- [ ] Define typed rules for undefined behavior, whitespace, includes, filters, sandbox, encoding, and diagnostics.
- [ ] Define typed override patches and mark security-sensitive fields as host-only.
- [ ] Publish rule metadata, defaults, documentation, and introspection schema.

## Rendering and safety

- [ ] Render immutable plain contexts with strict undefined behavior by default.
- [ ] Expose only explicitly registered filters, tests, globals, and safe value types.
- [ ] Resolve templates and fragments through the pack registry, never arbitrary filesystem paths.
- [ ] Record declared include dependencies and reject incompatible target-language fragments before rendering.
- [ ] Disable arbitrary Python attributes, imports, builtins, code execution, and hidden output emission.
- [ ] Support cancellation, deterministic diagnostics, text encoding, and session-scoped compiled-template caches.

## Quality and release

- [ ] Pass the shared template-engine conformance suite.
- [ ] Add sandbox escape, dynamic include, undefined value, whitespace, cache isolation, and cancellation tests.
- [ ] Prove rendering does not mutate contexts or registries.
- [ ] Version and publish independently from core and packs.
