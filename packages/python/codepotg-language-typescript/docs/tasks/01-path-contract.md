# TypeScript target path-contract tasks

## TS-PATH-001 — Target descriptors and validation

- [ ] Register `.ts`, `.tsx`, `.mts`, `.cts`, `.d.ts`, and supported longest-suffix behavior.
- [ ] Validate final filename legality, reserved platform names where target policy applies, and declaration/test conventions.
- [ ] Preserve the target suffix while the engine suffix is removed by core.
- [ ] Expose typed target metadata only through the public path-value registry when needed.

## TS-PATH-002 — Boundary tests

- [ ] Prove the adapter receives an already resolved destination.
- [ ] Prove it never parses `{recipe}` or `[expression]` source tokens.
- [ ] Prove it never chooses output directories.
- [ ] Prove it does not add or depend on semantic `fileName`, `filePath`, or `directory` properties.
- [ ] Test import resolution using final planned artifact paths.

**Acceptance:** removing the TypeScript adapter disables TypeScript target validation/rendering but leaves core path planning importable and functional for other targets.
