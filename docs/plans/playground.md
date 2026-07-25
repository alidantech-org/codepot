# Codepot Playground Plan

## Purpose

Build a working browser playground that lets developers explore Codepot contracts, inspect generated OpenAPI, experiment with template packs, preview generated files, and eventually run the same generation runtime used by CLI, editor, web, and MCP frontends.

The playground should begin with a low-risk browser-only experience and grow toward full generation without duplicating Codepot's compiler or runtime behavior.

## Product goals

The playground should help developers:

- learn the Codepot ecosystem interactively;
- edit real `codepot-openapi` contracts;
- compile contracts into OpenAPI JSON and YAML;
- inspect `x-codegen` metadata, resources, schemas, routes, entities, and frontends;
- edit `Codepotg.yaml`, `paths.yaml`, and Jinja templates;
- preview generated files before downloading them;
- understand diagnostics, template variables, generation plans, and file ownership;
- share examples and later save projects;
- use the same runtime boundaries as future CLI, editor, web, and MCP integrations.

## Recommended routes

```text
/playground
  Playground overview and example picker

/playground/openapi
  Browser-based codepot-openapi compilation and inspection

/playground/templates
  CodepotG task, paths.yaml, Jinja, and variable exploration

/playground/generate
  Full virtual generation preview

/projects
  Saved authenticated projects in a later phase

/templates
  Template marketplace and package discovery in a later phase
```

## Architecture direction

```text
Code editor and project UI
        ↓
frontend request and presentation layer
        ↓
shared compiler or runtime API
        ↓
in-memory artifacts, diagnostics, plans, and generated files
        ↓
preview, download, save, or publish
```

Frontends must not recreate compiler, inference, template, planning, or generation policy. They should send typed requests to reusable engines and present typed responses.

## Browser and server boundary

### Features that can run in the browser

A browser-only playground can support:

- CodeMirror contract editing;
- TypeScript syntax highlighting and editor diagnostics;
- browser-safe `codepot-openapi` contract compilation;
- in-memory OpenAPI JSON and YAML output;
- `x-codegen` metadata inspection;
- schema, route, resource, entity, and frontend explorers;
- downloadable OpenAPI output;
- template and configuration editing;
- virtual file previews;
- shareable encoded examples;
- Web Worker execution for responsive compilation.

### Features that currently require a server

The existing Python CodepotG runtime performs work that normal browsers cannot run directly:

- Python execution;
- OpenAPI JSONL indexing;
- Jinja rendering with CodepotG filters and contexts;
- template-pack discovery;
- dependency and import planning;
- filesystem operations;
- lifecycle and cleanup handling;
- optional project commands.

Full CodepotG generation therefore requires an isolated server worker until equivalent behavior is available through a browser-compatible shared runtime.

## Package restructuring for browser compilation

The current `codepot-openapi` package includes browser-safe domain behavior together with Node and CLI integrations. Before using it directly in the playground, separate those responsibilities.

### Proposed public entrypoints

```text
codepot-openapi/core
  Contract builders
  Schema registry
  Zod conversion
  OpenAPI compiler
  x-codegen compilation
  In-memory diagnostics
  No filesystem, process, terminal, or CLI dependencies

codepot-openapi/browser
  Browser compiler facade
  Web Worker helpers
  JSON and YAML serialization
  Playground diagnostics
  Browser-safe validation

codepot-openapi/node
  TypeScript configuration loading
  Filesystem output
  Node module resolution
  Redocly and Swagger Parser integrations

codepot-openapi/cli
  init
  generate
  validate
```

Example browser import:

```ts
import {
  compileOpenApi,
  definePackageConfig,
  defineVersionContract,
} from "codepot-openapi/browser";
```

## Phase 1: OpenAPI playground

### Goal

Deliver a useful browser-only playground without requiring a generation server.

### Features

- `/playground/openapi` route;
- CodeMirror editor for a real TypeScript contract;
- curated examples loaded from repository files;
- debounced compilation in a Web Worker;
- compile, reset, format, and example-selection controls;
- diagnostics panel with file, line, severity, and message;
- OpenAPI JSON and YAML tabs;
- schema, resource, route, entity, frontend, and `x-codegen` explorers;
- download JSON or YAML;
- copy output;
- shareable state using compressed URL data or a short-lived saved snippet;
- mobile and desktop responsive layouts;
- light and dark editor support.

### Security rules

- Never evaluate arbitrary code in the main browser thread.
- Restrict imports to approved playground modules.
- Run compilation in a dedicated Web Worker.
- Apply source-size and execution-time limits.
- Do not provide network, filesystem, process, or dynamic package installation access.

### Acceptance criteria

- A supported example compiles fully in the browser.
- Contract edits update diagnostics and OpenAPI output.
- The UI remains responsive while compiling.
- Output can be copied and downloaded.
- No server is required for the default flow.

## Phase 2: Template exploration

### Goal

Teach and inspect CodepotG template-pack behavior before enabling full server-backed generation.

### Features

- `/playground/templates` route;
- editors for `Codepotg.yaml`, `paths.yaml`, and Jinja files;
- real examples loaded from repository files;
- normalized-context fixture explorer;
- template variable catalog;
- selector and alias previews;
- output-path preview;
- static and raw file previews;
- managed, immutable, protected, and clean-root explanations;
- template rendering against controlled fixture contexts;
- Jinja syntax highlighting;
- linked documentation for each configuration concept.

### Important limitation

A simplified browser renderer must not be presented as complete CodepotG compatibility. Any preview-only implementation must clearly show which filters, inference behaviors, dependencies, lifecycle rules, or language adapters are unavailable.

### Acceptance criteria

- Developers can understand how a task, paths configuration, and template work together.
- Template variables and selected contexts are visible.
- Controlled fixtures can render safely in memory.
- The page clearly distinguishes preview behavior from full CodepotG execution.

## Phase 3: Server-backed CodepotG generation

### Goal

Run the actual CodepotG package in isolation and return a virtual file tree to the browser.

### Request flow

```text
Browser editors
  ├── OpenAPI input
  ├── Codepotg.yaml
  ├── paths.yaml
  └── Jinja templates
          ↓
Generation API
          ↓
isolated CodepotG worker
          ↓
virtual generated files and diagnostics
          ↓
file explorer, diffs, and ZIP download
```

### Server architecture

Use a dedicated worker service rather than executing generation inside the Next.js request process.

Each generation request should:

1. validate request size and file count;
2. create a fresh temporary workspace;
3. write only validated virtual inputs;
4. disable `before` and `after` project commands;
5. run CodepotG inside a container or equivalent sandbox;
6. apply CPU, memory, disk, process, and execution-time limits;
7. capture structured diagnostics and generated files;
8. return a virtual file tree and optional ZIP archive;
9. destroy the workspace immediately.

### Security requirements

- Never run user shell commands.
- Never run user Python modules.
- Do not expose host filesystem paths.
- Do not allow unrestricted network access.
- Restrict template and configuration sizes.
- Limit recursion, generated file count, output bytes, and render duration.
- Use non-root containers and read-only base images.
- Store no secrets in generation workers.
- Rate-limit anonymous requests.
- Scan and validate uploaded template archives.

### Acceptance criteria

- The actual CodepotG package generates files from playground inputs.
- The browser receives structured diagnostics and a virtual file tree.
- No user input can execute arbitrary commands or access the host.
- Temporary workspaces are always removed.
- Generated files can be inspected and downloaded as a ZIP.

## Phase 4: Browser-compatible codepotx runtime

### Goal

Move ordinary interactive planning and generation into the browser using the shared `codepotx` engine instead of maintaining a web-specific generator.

### Required browser platform

```text
codepotx/platform/browser
  In-memory filesystem
  Browser cache
  Web Worker execution
  Browser-safe hashing and codecs
  Cancellation
  Event transport
  ZIP export
  No shell commands
  No unrestricted Git or filesystem access
```

### Browser runtime flow

```text
Code editor
    ↓
codepotx runtime request
    ↓
browser memory platform
    ↓
compiled artifacts and generation plan
    ↓
rendered virtual files
    ↓
preview, diff, manifest inspection, ZIP download
```

### Capabilities

- authoring compilation;
- template-pack compilation;
- variable discovery;
- generation plans;
- dry runs;
- in-memory rendering;
- diagnostics and events;
- manifest previews;
- changed-file classification;
- ZIP export;
- cancellation;
- reuse by site, editor, MCP, tests, and other frontends.

### Acceptance criteria

- The same runtime operations work in Node and browser compositions.
- Browser generation does not duplicate planning or safety policy.
- Generated results match the shared runtime contract.
- Filesystem and command capabilities are explicitly absent or replaced by browser-safe adapters.

## Phase 5: Saved projects and collaboration

### Features

- authenticated saved playground projects;
- project versions and snapshots;
- share links with read-only or editable permissions;
- team workspaces;
- comments and review notes;
- saved generation outputs;
- reusable example galleries;
- import and export project archives;
- optional GitHub repository import and pull-request export.

### Server needs

A server remains useful for persistence, authentication, collaboration, GitHub integrations, large workloads, private packages, and audit history even after browser generation is available.

## Phase 6: Template marketplace

### Features

- public and private template packs;
- package metadata, versions, compatibility, and ownership;
- searchable framework, language, ORM, architecture, and use-case tags;
- dependency declarations between template packs;
- preview examples and generated output snapshots;
- publisher verification;
- vulnerability and policy checks;
- installation into playground projects;
- ratings, usage metrics, and documentation.

### Safety

Marketplace packages must never execute arbitrary commands in the browser or generation worker. Capabilities should be declared explicitly and reviewed before use.

## Phase 7: AI and MCP integration

### AI-assisted features

- explain diagnostics;
- suggest contract refinements;
- generate starter contracts from structured requirements;
- explain normalized contexts and template variables;
- help author `paths.yaml` and Jinja templates;
- compare generation plans;
- identify unsafe or contradictory configuration;
- propose migrations between prototype and runtime workflows.

### MCP surface

Expose typed tools for:

- reading project files and semantic artifacts;
- compiling contracts;
- listing schemas, resources, routes, and symbols;
- retrieving diagnostics;
- inspecting template variables;
- creating generation plans;
- rendering virtual files;
- downloading approved outputs.

AI tools must use the same runtime operations and safety policy as human-facing frontends.

## Phase 8: Codepot Lang playground

### Features

- Codepot Lang editor;
- parser and semantic diagnostics;
- formatter;
- module and symbol explorer;
- target-neutral IR viewer;
- standard-library browser;
- hover, completion, and signature information;
- browser-hosted compiler through WebAssembly or a server compiler service;
- future generation and interpreter previews.

The language playground should reuse compiler crates rather than recreating parsing or semantic analysis in TypeScript.

## Editor choice

Use CodeMirror 6 for the initial playground because it is already integrated into the site, works well with React and Next.js, supports multiple languages, has a smaller footprint than Monaco, and can be configured for mobile layouts.

Monaco may be reconsidered later if the playground needs deep TypeScript language-service behavior that cannot be delivered cleanly through CodeMirror and Web Workers.

## Web Worker strategy

Compilation and rendering that can run in the browser should execute outside the main UI thread.

Workers should provide:

- typed request and response messages;
- cancellation tokens;
- execution timeouts;
- source-size limits;
- deterministic diagnostics;
- progress events;
- reusable worker pools only when isolation remains safe.

## State management

Initial playground state can remain local:

- editor drafts in React state;
- selected example in URL search parameters;
- optional compressed share state in the URL;
- browser persistence through IndexedDB for local drafts.

Saved cloud projects should be introduced only after authentication and project ownership are designed.

## Observability

Track:

- compile and generation duration;
- worker startup time;
- error categories;
- memory and output sizes;
- cancellation and timeout rates;
- selected examples;
- download and share actions;
- server-worker queue duration;
- sandbox failures.

Do not collect source content unless users explicitly save a project and the privacy policy clearly explains storage.

## Accessibility and responsiveness

- Support keyboard-only editing and controls.
- Preserve visible focus states.
- Label diagnostics and output tabs correctly.
- Provide high-contrast light and dark themes.
- Stack editors, inspectors, and file trees on small screens.
- Allow panels to collapse or switch through tabs on mobile.
- Respect reduced-motion settings.
- Keep horizontal scrolling inside editors and code views, not on the page.

## Milestones

### Milestone 1: architecture preparation

- [ ] Audit Node-only dependencies in `codepot-openapi`.
- [ ] Define `core`, `browser`, `node`, and `cli` boundaries.
- [ ] Add browser-safe package exports.
- [ ] Add tests proving browser bundles contain no Node built-ins.
- [ ] Define playground request, result, and diagnostic contracts.

### Milestone 2: OpenAPI playground MVP

- [ ] Create `/playground/openapi`.
- [ ] Add contract editor and examples.
- [ ] Add Web Worker compilation.
- [ ] Add diagnostics.
- [ ] Add JSON/YAML output.
- [ ] Add schema and route explorers.
- [ ] Add downloads and reset controls.
- [ ] Add mobile and dark-mode support.

### Milestone 3: template explorer

- [ ] Create `/playground/templates`.
- [ ] Add real `Codepotg.yaml`, `paths.yaml`, and Jinja examples.
- [ ] Add normalized-context fixtures.
- [ ] Add variable and selector explorers.
- [ ] Add controlled preview rendering.
- [ ] Clearly label compatibility limitations.

### Milestone 4: isolated CodepotG generation

- [ ] Design the generation API.
- [ ] Build a non-root sandbox worker image.
- [ ] Disable project commands.
- [ ] Add resource and time limits.
- [ ] Return diagnostics and virtual files.
- [ ] Add file explorer and ZIP download.
- [ ] Add rate limits and abuse protection.

### Milestone 5: browser codepotx runtime

- [ ] Define browser platform services.
- [ ] Add an in-memory browser filesystem.
- [ ] Move runtime execution into Web Workers.
- [ ] Add planning, rendering, events, and cancellation.
- [ ] Add ZIP export.
- [ ] Add compatibility tests against Node runtime results.

### Milestone 6: persistence and collaboration

- [ ] Add authentication.
- [ ] Add saved projects and snapshots.
- [ ] Add share permissions.
- [ ] Add team workspaces.
- [ ] Add optional GitHub import and export.

### Milestone 7: marketplace and AI

- [ ] Define template package metadata and permissions.
- [ ] Add marketplace browsing and installation.
- [ ] Add security and compatibility checks.
- [ ] Add MCP tools over shared runtime operations.
- [ ] Add AI-assisted explanations and authoring workflows.

### Milestone 8: Codepot Lang playground

- [ ] Decide WebAssembly versus compiler service.
- [ ] Add language editor and diagnostics.
- [ ] Add formatting and semantic inspection.
- [ ] Add standard-library and IR explorers.
- [ ] Reuse compiler and analysis crates directly.

## Recommended starting point

Start with the browser-only `codepot-openapi` playground.

It provides immediate value, requires no generation server for its default workflow, and forces a useful separation between browser-safe compiler behavior and Node-specific CLI integrations.

After that, add template exploration and an isolated CodepotG generation service. Long-term interactive generation should move toward the browser-compatible `codepotx` runtime so the site, CLI, editor, MCP server, tests, and future frontends share one engine instead of maintaining separate implementations.
