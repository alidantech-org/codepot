# Dryv TypeScript Client Contract

`src/index.ts` is the transport-neutral TypeScript reference contract for `dryv.api/v1`. It exists so VS Code, web, desktop and agent hosts can share the same build/artifact vocabulary without importing or reimplementing Dryv Runtime.

This directory intentionally has **no `package.json` yet**. Adding a new pnpm workspace importer requires regenerating the repository lockfile with pnpm in a real checkout. The migration environment could not run pnpm, so the source contract is kept outside the active workspace rather than making frozen installs nondeterministic.

## Ownership

The TypeScript client knows:

- versioned build requests;
- logical resources;
- previous managed-output/project snapshot facts;
- build-result metadata;
- bounded artifact-content events;
- write-instruction vocabulary;
- build cancellation.

It does not know:

- Canonical IR implementation classes;
- Runtime Features;
- template engines;
- Author Backend implementation details;
- project filesystem APIs;
- local `apply_complete` behavior.

A VS Code or desktop host can pair this transport contract with its own local resource/apply implementation. A browser can pair it with browser-supported project storage. All clients still send the same `dryv.api/v1` messages.

When this reference is promoted to a publishable workspace package, run pnpm in a real checkout and commit the generated lockfile change together with `package.json`/`tsconfig.json`.
