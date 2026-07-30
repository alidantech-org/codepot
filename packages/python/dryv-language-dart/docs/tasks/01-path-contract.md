# Dart target path and import-contract tasks

## DART-PATH-001 — Target descriptor and validation

- [ ] Register `.dart` target behavior and final filename validation.
- [ ] Validate Dart library/part filename restrictions without selecting destination directories.
- [ ] Preserve `.dart` while core removes the engine suffix.
- [ ] Expose typed target metadata only through the public expression registry.

## DART-PATH-002 — Core boundary tests

- [ ] Prove the adapter receives an already resolved destination and selection scope.
- [ ] Prove it never parses `{selectionKey}`, `{root}`, `(expression)`, or `((literal))` source syntax.
- [ ] Prove it never evaluates fixed selectors or chooses output directories.
- [ ] Prove it does not add or depend on semantic `fileName`, `filePath`, or `directory` fields.

## DART-PATH-003 — Planned imports and exports

- [ ] Consume immutable generated import plans created from explicit selection `imports` mappings.
- [ ] Calculate relative and `package:` URIs from final planned paths and project/package metadata.
- [ ] Render least-required symbols, prefixes, aliases, and deterministic import ordering.
- [ ] Consume ordered barrel/library export descriptors created from selection `exports` and declared `symbols`.
- [ ] Support explicit Dart exports without scanning generated files.
- [ ] Reject Dart-level URI, prefix, and symbol conflicts after core dependency validation.

**Acceptance:** Dart filename/import/export behavior is independently installable and never owns the pack filesystem, selector registry, or output-folder composition.
