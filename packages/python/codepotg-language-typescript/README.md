# codepotg-language-typescript

Pure-Python TypeScript target validation and module-path facts for CodepotG v2.

## Baseline

- Language baseline: conservative TypeScript identifier and module-specifier subset.
- Behavior version: `1`.
- Date verified: 2026-07-27.
- Supported output suffixes: `.ts`, `.tsx`, `.mts`, `.cts`, `.d.ts`, `.d.mts`, `.d.cts` using longest-known matching.
- Identifier subset: ASCII by default; an explicit specification-oriented Unicode-category policy is available.
- Module forms: relative, configured aliases, validated npm-style bare packages, and validated explicit module specifiers.
- Unsupported: runtime `.js`/`.mjs`/`.cjs` rewriting, semantic type-only/value-use inference, symbol grouping, import/export rendering, framework behavior, planner configuration decoding, and diagnostics on `ModulePathFacts`.

The package returns immutable descriptors, diagnostics, and `ModulePathFacts`. Templates own every emitted TypeScript character.
