# Task 27 — CodepotG five additional language adapters

Status: [-]
Branch: `chatgpt/codepotx-restart`
Depends on: Task 25 complete template-variable contract

## Goal

Add production-ready adapter foundations for five widely used API/client languages after TypeScript and Dart: Python, Java, C#, Go, and Rust. Each adapter must consume the same language-neutral API contract, preserve the complete template-variable surface, provide target metadata and post-generation guidance, and be proven by inspectable fixtures.

## Required work

- [x] Extract a reusable portable adapter builder from the complete typed debug contract without changing existing TypeScript or Dart behavior.
- [x] Add Python adapter and aliases.
- [x] Add Java adapter and aliases.
- [x] Add C# adapter and aliases.
- [x] Add Go adapter and aliases.
- [x] Add Rust adapter and aliases.
- [x] Give every adapter deterministic project/package metadata and target-specific diagnostics.
- [x] Ensure discovery registers canonical names and aliases without collisions.
- [x] Add one reviewable fixture project per new language.
- [-] Replace variable-probe-only fixtures with representative target-language templates that generate compilable package structures.
- [-] Add generated representative examples and safe write policies for every target.
- [x] Test all adapters against the same OpenAPI fixture and variable probe templates.
- [x] Test complete generation, cache reuse, output uniqueness, physical writes, and language metadata.
- [-] Add target-specific type, import, enum, model, request, response, and operation enrichment for every adapter.
- [-] Add language-specific import planners rather than falling back to Markdown import rendering.
- [-] Add target package metadata and build files: Python packaging, Java Maven, .NET project, Go module, and Rust Cargo.
- [-] Validate generated fixtures with the native compiler or formatter when the tool is installed.
- [ ] Add complete package/module entry points and native module registries.
- [ ] Verify request and response types compile in representative operations.
- [ ] Document supported languages and adapter-authoring rules.

## Implemented evidence awaiting validation

- Typed target systems cover scalar, format, collection, map, nullability, file, package, and source-layout conventions.
- Generated fixtures now include manifests, native models, enums, operation clients, and registry-planned imports.
- Native validation tests run Python compileall, javac, dotnet build, gofmt, and rustfmt when available.
- Existing TypeScript and Dart planners remain selected before the portable fallback planner.

## Safety constraints

- Keep inference language-neutral.
- Do not copy TypeScript syntax into other adapters.
- Language adapters may enrich names/types/import text, but must not re-parse OpenAPI or `x-codegen` dictionaries.
- Keep post-actions informational; do not execute package managers or formatters automatically.
- Prototype metadata-only adapters do not satisfy this task; completion requires target-specific generation and inspectable packages.

## Validation

- [ ] Adapter discovery tests pass.
- [ ] Five language fixture suites pass.
- [ ] Native syntax/build validation passes where toolchains are available.
- [ ] Existing TypeScript, Dart, and debug adapter tests pass.
- [ ] Ruff passes.
- [ ] Complete package suite passes.
