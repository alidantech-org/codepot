# Task 27 — CodepotG five additional language adapters

Status: [-]
Branch: `chatgpt/codepotx-restart`
Depends on: Task 25 complete template-variable contract

## Goal

Add production-ready adapter foundations for five widely used API/client languages after TypeScript and Dart: Python, Java, C#, Go, and Kotlin. Each adapter must consume the same language-neutral API contract, preserve the complete template-variable surface, provide target metadata and post-generation guidance, and be proven by inspectable fixtures.

## Required work

- [ ] Extract a reusable portable adapter builder from the complete typed debug contract without changing existing TypeScript or Dart behavior.
- [ ] Add Python adapter and aliases.
- [ ] Add Java adapter and aliases.
- [ ] Add C# adapter and aliases.
- [ ] Add Go adapter and aliases.
- [ ] Add Kotlin adapter and aliases.
- [ ] Give every adapter deterministic project/package metadata and target-specific diagnostics.
- [ ] Ensure discovery registers canonical names and aliases without collisions.
- [ ] Add one realistic, reviewable fixture pack per new language.
- [ ] Add generated representative examples and safe write policies.
- [ ] Test all adapters against the same OpenAPI fixture and variable probe templates.
- [ ] Test complete generation, cache reuse, output uniqueness, physical writes, and language metadata.
- [ ] Document supported languages and adapter-authoring rules.

## Safety constraints

- Keep inference language-neutral.
- Do not copy TypeScript syntax into other adapters.
- Language adapters may enrich names/types/import text, but must not re-parse OpenAPI or `x-codegen` dictionaries.
- Keep post-actions informational; do not execute package managers or formatters automatically.

## Validation

- [ ] Adapter discovery tests pass.
- [ ] Five language fixture suites pass.
- [ ] Existing TypeScript, Dart, and debug adapter tests pass.
- [ ] Ruff passes.
- [ ] Complete package suite passes.
