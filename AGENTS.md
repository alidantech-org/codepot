# Codepot contributor instructions

Read these files before changing the active `codepotx` implementation:

1. `agents/README.md`
2. `agents/ARCHITECTURE.md`
3. `agents/RULES.md`
4. `agents/WORKFLOW.md`
5. the active file under `agents/tasks/`

## Non-negotiable rules

- Work from the active `chatgpt/*` branch and never modify `packages/nodejs/codepotx-old` except for explicitly approved archival corrections.
- Open a GitHub issue before implementation begins. Close it immediately after the linked task is complete and validated; never leave a completed task's issue open.
- Update the matching task file with status, issue, validation evidence, and commit SHA.
- Define stable contracts, types, interfaces, ports, requests, and results before implementing classes or functions.
- Keep type/interface declarations separate from implementation files.
- Preserve the old TypeScript authoring API tooth by tooth. Existing contracts should migrate primarily by importing Codepot APIs and `z` from `codepotx`.
- Authoring compiles directly to the stable Codepot authoring artifact. OpenAPI is not an intermediate requirement for template generation.
- Keep authoring, templating, and generation autonomous. They communicate through shared contracts and injected ports.
- Runtime is the composition root. Use dependency injection and dependency inversion; do not use global mutable registries or service locators.
- Use the event bus only for progress, diagnostics, tracing, and observation. Required control flow must use typed method calls and returned results.
- Keep the CLI external and thin. It must not parse project files, compile contracts, render templates, or write generated files itself.
- Centralize filesystem, YAML/JSON, module loading, source resolution, hashing, caching, command execution, and changed-aware writing behind platform ports.
- Use extensionless TypeScript imports and internal `@/*` aliases. Do not expose internal aliases in published output.
- Do not begin a later phase before its dependencies and validation gates in `agents/tasks/00-roadmap.md` are complete.
