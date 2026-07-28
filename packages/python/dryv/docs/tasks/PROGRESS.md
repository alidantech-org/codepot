# Dryv progress log

| Date | Commit | Work | Status | Evidence |
|---|---|---|---|---|
| 2026-07-27 | `6d97e6f` and supporting commits | Connected CodepotG v2 package baseline before rebrand | verified baseline | 461 passed, 1 skipped across core, authoring, Jinja, TypeScript, and Dart packages; Ruff checks and formatting passed; generated TypeScript and Dart manual projects compiled/analyzed successfully. |
| 2026-07-28 | `b1049397` | Rename the new package family to Dryv and remove the retired source package | implementation checkpoint | Package directories, import namespaces, distributions, entry-point groups, manifests, project files, API versions, state paths, examples, tests, and documentation were renamed. The removed package is no longer tracked. Post-rebrand verification remains required. |
| 2026-07-28 | current cleanup series | Remove stale source expectations and pre-rebrand documentation | in progress | Manual plugin graph now expects only IR, TypeScript, Dart, and Jinja. Active boundary tests and manual routes were updated. Obsolete audit and implementation-prompt files were removed. |

## Current architecture

```text
dryv
├── canonical IR and diagnostics
├── project and pack configuration
├── plugin discovery
├── planning and rendering coordination
├── managed output and ownership state
└── reusable runtime operations

dryv-cli
└── thin command-line interface over dryv

dryv-author
└── typed Python authoring to in-memory Dryv IR

dryv-template-jinja
└── sandboxed deterministic rendering

dryv-language-typescript
└── TypeScript validation and module-path facts

dryv-language-dart
└── Dart validation and URI/path facts
```

## Immediate verification gate

Run the renamed packages in dependency order:

```bash
cd packages/python/dryv
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build
```

Then repeat for:

```text
dryv-author
dryv-template-jinja
dryv-language-typescript
dryv-language-dart
```

Finally install all real wheels into a fresh environment and verify entry-point discovery, direct IR generation, Python authoring generation, TypeScript compilation, Dart analysis, deterministic reruns, and managed-file protection.

## Next architecture work

1. Extract `dryv-cli` from the runtime distribution.
2. Introduce a public `DryvRuntime` facade.
3. Add `validate_project`, `validate_pack`, and `validate_plugin` runtime operations.
4. Add direct Python contract-provider support so authoring does not require a transport file.
5. Remove compatibility transport exports from `dryv-author` after migration.
6. Build the first Dryv Cookbook recipes.

## Release rule

No package is release-ready after the rename until lint, formatting, tests, build, wheel inspection, isolated installation, connected generation, and final old-name/source-reference scans pass on the exact branch head.
