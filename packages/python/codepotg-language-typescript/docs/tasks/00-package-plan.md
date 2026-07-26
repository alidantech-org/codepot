# TypeScript language-adapter tasks

## Foundation

- [ ] Add isolated package metadata, entry point, supported extension descriptors, and compatibility metadata.
- [ ] Add architecture tests proving no framework, source-adapter, template-engine, CLI, filesystem, or command dependencies.
- [ ] Implement adapter factory and immutable instance context.

## Locked configuration contract

- [ ] Define typed rules for identifiers, naming, files, modules, imports, exports, types, literals, comments, and formatting.
- [ ] Define typed override patches with replace, append, prepend, merge-by-key, union, remove, reset, and denied policies.
- [ ] Publish rule-path metadata, defaults, documentation, and introspection schema.
- [ ] Validate conflicting aliases, extensions, module modes, and import policies.

## Syntax services

- [ ] Implement identifiers, escaping, reserved words, and naming transforms.
- [ ] Implement primitives, arrays, maps, unions, intersections, generics, functions, nullable and optional types.
- [ ] Implement deterministic literals and documentation comments.
- [ ] Implement named, default, namespace, type-only, side-effect, and aliased imports and exports.
- [ ] Implement relative, alias, package, project-path, and barrel module resolution with deduplication and collision handling.
- [ ] Support `.ts`, `.tsx`, `.mts`, `.cts`, and declaration-file conventions using longest-suffix target detection.

## Quality and release

- [ ] Pass the shared language-adapter conformance suite.
- [ ] Add focused tests for every rule category and import edge case.
- [ ] Prove immutable neutral IR input and deterministic output.
- [ ] Prove the adapter contains no NestJS, Next.js, React, Node-project, or pack assumptions.
- [ ] Version and publish independently from core and template packs.
