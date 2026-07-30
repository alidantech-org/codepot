# Dryv parallel work registry

This registry coordinates changes across the Dryv Python package family. Work happens only on explicitly approved existing branches; agents must not create branches unless the user asks.

## Package lanes

| Package | Responsibility | Current focus |
|---|---|---|
| `dryv` | canonical IR, runtime, plugin contracts, planning, generation coordination, managed output | remove embedded CLI ownership and publish a clean runtime facade |
| `dryv-cli` | command-line interface over public runtime operations | create package, move existing plan/generate commands, add validators incrementally |
| `dryv-author` | typed Python declarations compiled to in-memory Dryv IR | remove duplicate transport ownership and expose direct runtime integration |
| `dryv-template-jinja` | sandboxed deterministic template engine | maintain public engine contract and bounded rendering |
| `dryv-language-typescript` | TypeScript target validation and module-path facts | maintain target contract and official pack integration |
| `dryv-language-dart` | Dart target validation and URI/path facts | maintain target contract and official pack integration |

## Active architectural work

| Task | Owner | Status | Scope |
|---|---|---|---|
| DRYV-REBRAND | Dryv package family | in progress | package names, imports, entry points, manifests, docs, examples, and ownership state |
| DRYV-RUNTIME | `dryv` | planned | `DryvRuntime` facade, validation services, contract providers, planning, generation, state inspection |
| DRYV-CLI | `dryv-cli` | planned | thin CLI package using only public runtime operations |
| DRYV-AUTHOR | `dryv-author` | in progress | in-memory contract result, runtime-owned transport, Python contract provider integration |
| DRYV-COOKBOOK | documentation | planned | executable recipes for first project, packs, plugins, safe generation, and reproducibility |

## Dependency direction

```text
dryv-cli ----------------------> dryv
dryv-author -------------------> dryv
dryv-template-jinja -----------> dryv
dryv-language-typescript ------> dryv
dryv-language-dart ------------> dryv
```

`dryv` must never depend on `dryv-cli` or `dryv-author`.

## Claim procedure

1. Select a task whose dependencies are satisfied.
2. Record the exact files or subsystem being changed.
3. Avoid overlapping implementation files across active agents.
4. Keep tests beside the code that changes.
5. Move work to review only after focused verification passes.
6. Mark complete only after the complete package gate passes.

## Design gates

- One closed, typed, versioned Dryv IR.
- Authoring frontends compile into public IR and do not create parallel semantic graphs.
- Templates, macros, partials, and static files own every emitted character.
- Language plugins validate names, paths, and module facts; they do not render syntax.
- Plugin packages depend only on public Dryv contracts.
- The runtime owns coordination; interfaces remain thin adapters.
- Canonical JSON/YAML is optional runtime transport, not a required intermediate file.
- Planning completes before rendering or filesystem mutation.
- Managed writes protect human files and update state transactionally.
- Full deterministic generation remains the correctness reference for incremental work.
- No GitHub automation is created or modified.

## Blocker rule

A blocked task records the exact missing public contract, operation, or test fixture. Generic statements such as “waiting for core” are insufficient.
