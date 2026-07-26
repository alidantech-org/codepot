# 06 — Compatibility and staged rewrite

## Legacy project configuration

The current project format uses `allow`, `tasks`, `input`, project-level `language`, `templateDir`, `output`, `clean`, and before/after commands. A legacy decoder maps it into the canonical project model:

- `tasks.<name>` becomes `packs.<name>`;
- `input` becomes a named source reference;
- `templateDir` becomes the pack source;
- `output` becomes the pack-instance output root;
- project-level `language` is validated for compatibility but removed from canonical orchestration because templates own target syntax;
- commands and clean scopes retain their project-owned trust and lifecycle meanings.

Legacy files continue to generate through the compatibility decoder and receive migration diagnostics. Generation never rewrites them automatically. `codepotg config migrate` produces the new form explicitly and supports `--check`.

## Legacy paths.yaml

`CodepotgPack.yaml` replaces and expands `paths.yaml`. The compatibility decoder maps:

- metadata to pack metadata;
- write policy to pack lifecycle policy;
- selections unchanged into typed selection declarations;
- emissions into discovered template descriptors;
- barrels into ordinary authored template descriptors with barrel role;
- folders into file-pattern defaults and selection fan-out;
- global imports into target-language rules;
- template extension and raw-file behavior into content discovery and engine rules.

A migrated pack must use a real barrel template file. Existing system-generated barrel behavior remains available only through a generated compatibility template during migration. Static files become emitted by default subject to ignore patterns.

`codepotg pack migrate` creates `CodepotgPack.yaml` without deleting `paths.yaml` unless explicitly requested.

## Staged rewrite sequence

1. Package foundation and architecture tests.
2. Public Python API, diagnostics, events, and isolated sessions.
3. Location-aware configuration documents and versioned registry.
4. Typed project configuration and legacy project decoder.
5. Typed pack manifest and legacy paths decoder.
6. Unified file discovery, static content, file patterns, and selections.
7. Binding catalog, semantic imports, locked rules, and override protocol.
8. Plugin ports, entry-point discovery, and instance registry.
9. Neutral IR and OpenAPI source adapter.
10. Template invocation and dependency planner.
11. Transactional writer and content-addressed cache.
12. TypeScript and Dart language adapters.
13. Sandboxed Jinja adapter.
14. TypeScript, Dart, and Flutter pack migrations.
15. Setup/configure workflow, typed actions, and command security.
16. Thin CLI, asynchronous facade, and MCP-ready operations.
17. Side-by-side compatibility fixtures, output review, and release cutover.

Each stage lands as a coherent commit with focused tests, recorded SHA, completed tasks, next-stage notes, and known risks.
