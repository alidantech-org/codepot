# Dryv progress log

| Date | Commit | Work | Status | Evidence |
|---|---|---|---|---|
| 2026-07-27 | `6d97e6f` and supporting commits | Connected CodepotG v2 package baseline before rebrand | verified baseline | 461 passed, 1 skipped across core, authoring, Jinja, TypeScript, and Dart packages; Ruff and formatting passed; generated TypeScript and Dart projects compiled/analyzed. |
| 2026-07-28 | `b1049397` | Rename the new package family to Dryv and remove the retired source package | implementation checkpoint | Package directories, namespaces, distributions, entry-point groups, manifests, state paths, examples, tests, and docs were renamed. Post-rebrand verification remains required. |
| 2026-07-28 | cleanup series through `0f7b47db` | Remove stale source expectations and pre-rebrand documentation | implemented; verification required | Active manual routes use canonical IR and Python authoring. Obsolete adapter expectations, prompts, and audits were removed. |
| 2026-07-28 | runtime/CLI series after `0f7b47db` | Expose `DryvRuntime` and extract `dryv-cli` | implemented; verification required | Core console script and embedded CLI removed. Runtime facade, plugin snapshot, standalone Click/Rich/Questionary CLI, borderless trees, spinners, plain JSON, prompt safety, architecture tests, distribution tests, and placeholder cleanup added. |

## Current architecture

```text
dryv
├── DryvRuntime
│   ├── snapshot
│   ├── plan
│   ├── generate
│   └── generate_to_files
├── canonical IR and diagnostics
├── project and pack configuration
├── plugin composition
├── planning and rendering coordination
└── managed output and ownership state

dryv-cli
├── Click command tree
├── Rich presentation and spinners
├── Questionary confirmation
└── public Dryv runtime consumption only

dryv-author
└── typed Python authoring to in-memory Dryv IR

dryv-template-jinja
└── sandboxed deterministic rendering

dryv-language-typescript
└── TypeScript validation and module-path facts

dryv-language-dart
└── Dart validation and URI/path facts
```

## Runtime/CLI boundary evidence

Implemented architecture tests require:

- no `dryv.cli` package or core console script;
- no Rich, Questionary, Click, Typer, or argparse dependency/import in core;
- no direct `print()` or `input()` calls;
- `dryv-cli` owns the `dryv` entry point;
- no private core imports from the CLI;
- no Rich panels or box-border layouts;
- no `.gitkeep` beside implemented CLI code;
- machine JSON contains no ANSI styling;
- non-interactive generation never waits for a prompt.

Stale `.gitkeep` files were removed from implemented core API, application, configuration, domain IR/generation, infrastructure, plugins, ports, runtime, architecture-test, and unit-test directories. Placeholder-only fixture directories remain untouched.

## Immediate verification gate

Run the runtime and CLI first:

```bash
cd packages/python/dryv
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build

cd ../dryv-cli
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build
```

Then repeat package verification for authoring, Jinja, TypeScript, and Dart. Finally install all real wheels together and verify entry-point discovery, CLI ownership, direct IR generation, Python authoring generation, TypeScript compilation, Dart analysis, deterministic reruns, and managed-file protection.

## Next architecture work

1. Add `validate_project`, `validate_pack`, and `validate_plugin` runtime operations, then expose matching thin CLI commands.
2. Add direct Python and host-supplied contract providers.
3. Add runtime plan/state explanation APIs before adding CLI inspection commands.
4. Remove compatibility transport exports from `dryv-author` after migration.
5. Build the first Dryv Cookbook recipes.

## Release rule

No package is release-ready until lint, formatting, tests, build, wheel inspection, isolated installation, connected generation, and final old-name/source-reference scans pass on the exact branch head.
