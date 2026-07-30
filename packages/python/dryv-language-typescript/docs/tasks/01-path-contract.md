# TypeScript target path and import-contract tasks

## TS-PATH-001 — Target descriptors and validation

- [ ] Register `.ts`, `.tsx`, `.mts`, `.cts`, `.d.ts`, and supported longest-suffix behavior.
- [ ] Validate final filename legality, reserved platform names where target policy applies, and declaration/test conventions.
- [ ] Preserve the target suffix while core removes the engine suffix.
- [ ] Expose typed target metadata only through the public expression registry when needed.

## TS-PATH-002 — Core boundary tests

- [ ] Prove the adapter receives an already resolved destination and selection scope.
- [ ] Prove it never parses `{selectionKey}`, `{root}`, `(expression)`, or `((literal))` source syntax.
- [ ] Prove it never evaluates fixed selectors or chooses output directories.
- [ ] Prove it does not add or depend on semantic `fileName`, `filePath`, or `directory` properties.

## TS-PATH-003 — Planned imports and exports

- [ ] Consume immutable generated import plans created from explicit selection `imports` mappings.
- [ ] Calculate legal relative, alias, or package module specifiers from final planned paths.
- [ ] Render least-required value imports, type-only imports, aliases, grouping, and deterministic ordering.
- [ ] Consume ordered barrel export descriptors created from selection `exports` and declared `symbols`.
- [ ] Support wildcard, explicit, and type-only exports without discovering files from the filesystem.
- [ ] Reject target-level symbol/import conflicts that remain after core dependency validation.

**Acceptance:** removing the TypeScript adapter disables TypeScript filename/import/export behavior but leaves core selection, path, and dependency planning functional for other targets.
