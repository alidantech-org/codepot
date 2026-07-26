# Dart language-adapter tasks

## Foundation

- [ ] Add isolated package metadata, entry point, `.dart` target descriptor, and compatibility metadata.
- [ ] Add architecture tests proving Flutter, source, engine, CLI, filesystem, and command independence.
- [ ] Implement adapter factory and immutable instance context.

## Locked configuration contract

- [ ] Define typed rules for identifiers, naming, files, libraries, imports, exports, null safety, types, literals, comments, and formatting.
- [ ] Define typed override patches and field-specific merge or denial policies.
- [ ] Publish defaults, rule-path documentation, and introspection schema.
- [ ] Validate package names, SDK constraints, import policies, and incompatible language options.

## Syntax services

- [ ] Implement identifiers, reserved words, casing, and escaping.
- [ ] Implement primitives, records, lists, maps, sets, generics, functions, futures, streams, nullable and required semantics.
- [ ] Implement deterministic literals, annotations where language-level, and documentation comments.
- [ ] Implement relative, `package:`, project-path, deferred, prefix, show, and hide import behavior.
- [ ] Implement export planning and duplicate or prefix conflict resolution.

## Quality and release

- [ ] Pass the shared language-adapter conformance suite.
- [ ] Add focused null-safety, generic, import, and package-path tests.
- [ ] Prove deterministic output and immutable IR input.
- [ ] Prove no Flutter widgets, packages, folder assumptions, or framework rules exist here.
- [ ] Version and publish independently from core and Dart/Flutter packs.
