# 02 — Typed configuration and pack contracts

## Two primary authored files

CodepotG v2 keeps the user-facing model simple:

- `codepotg.yaml` contains all project-owned configuration.
- `CodepotgPack.yaml` contains all pack-owned configuration and replaces the responsibilities of `paths.yaml`.

Raw YAML dictionaries never enter application or domain logic. Infrastructure parses a location-aware document tree, a versioned decoder produces typed models, migrations create the current canonical model, semantic validation resolves plugins and pack contracts, and only then is a generation plan compiled.

## Project configuration

A project registers sources, toolchains, security, global commands, and named pack instances. It does not select a global language.

```yaml
apiVersion: codepotg.dev/v2
kind: Project
metadata:
  name: example
sources:
  api:
    adapter: openapi
    path: ./openapi.yaml
toolchains:
  node:
    packageManager: pnpm
security:
  commands:
    project: allow
    packs: requireApproval
commands:
  before: []
  after: []
packs:
  server:
    use:
      path: ./packs/server
    source: api
    output:
      root: ./_
    options: {}
    bindings: {}
    overrides: {}
    commands:
      before: []
      after: []
```

The current `tasks` entries migrate to named `packs`. Project-global commands run once around the complete pack sequence. Project-owned commands under a pack instance run around that instance. Pack-owned commands come from `CodepotgPack.yaml` and retain their lower trust level.

## Pack manifest

`CodepotgPack.yaml` is the typed successor to `paths.yaml`. It owns metadata, content discovery, ignore patterns, file-pattern defaults, selections, template descriptors, language and engine rules, bindings, dependency requirements, setup, lifecycle policy, and pack commands.

A pack is heterogeneous. It may include TypeScript, Dart, YAML, Markdown, SQL, JSON, images, and plain static files. A project and a pack never have one selected language.

## Template ownership of language

A template normally uses `file-name.<target-extension>.<template-engine-extension>`:

```text
user.ts.jinja
client.dart.jinja
config.yaml.jinja
README.md.jinja
```

The engine suffix answers how the source is rendered. The preceding recognized suffix answers what target syntax is produced. Longest-known-suffix matching supports names such as `types.d.ts.jinja` and `component.test.tsx.jinja`. Ambiguous files such as `Dockerfile.jinja` may declare an explicit target.

## Unified file model

Pack content is discovered once and classified as:

- `template` — rendered and emitted;
- `barrel` — an ordinary authored template receiving planned exports;
- `static` — copied without rendering;
- `partial` — available to templates but not emitted;
- `documentation` — pack guidance and examples.

Non-template files are emitted by default because `.gitignore`, `.env.example`, `LICENSE`, images, fixtures, and many configuration files need no rendering. Gitignore-style `ignore` patterns or `.codepotgignore` exclude pack-author files. Explicit file declarations configure the discovered descriptor and must never create a duplicate emission.

## Bindings

The pack owns a typed, documented binding catalog. Each template explicitly lists the bindings it consumes. The project supplies project-specific values under its pack instance.

```yaml
# CodepotgPack.yaml
bindings:
  baseRepository:
    kind: import
    language: typescript
    required: true
    acceptedSources: [module, projectPath, barrel]
    whenMissing: placeholder

templates:
  repository:
    file: templates/repository.ts.jinja
    uses:
      bindings: [baseRepository]
```

```yaml
# codepotg.yaml
packs:
  persistence:
    use: ./packs/persistence
    bindings:
      baseRepository:
        symbol: BaseRepository
        from:
          barrel: "@modules/common"
```

Binding kinds include import, symbol, project path, text, text file, configuration value, environment reference, artifact reference, package name, and namespace. A default barrel or binding group can satisfy several imports and the language adapter deduplicates them.

Missing bindings support `prompt`, `placeholder`, `omit`, `skipTemplate`, or `error`. Flexible local generation may continue with warnings and required actions; strict CI mode may reject unresolved requirements.

## Locked rules and overrides

Core defines the configuration and override protocol. Language and template-engine adapters publish typed defaults, rule models, override patches, supported rule paths, merge policies, documentation metadata, and validators. Unknown fields are errors. Generic recursive dictionary merging is forbidden.

Standard merge policies include replace, append, prepend, merge-by-key, union, remove, reset-to-default, and not-overridable. Adapter hard restrictions cannot be weakened by packs. Packs may further restrict the fields a project is allowed to override.

Effective precedence is deterministic:

1. adapter defaults;
2. pack rules;
3. template-local rules;
4. project global language or engine override;
5. project pack-instance override;
6. permitted project template override.

## Pack traits, dependencies, and setup

Packs use composable traits rather than one rigid type. A pack may create a full project, own a standalone folder or package, contribute files to an existing project, require dependencies, require project bindings, or provide fragments.

Known ecosystem sections such as Node and Dart use typed schemas. Packs declare desired dependencies separately from installation actions. Projects select toolchains such as npm, pnpm, Yarn, or Pub; pack constraints are resolved against the existing project and lockfiles.

`codepotg configure` reads pack setup contracts, inspects the project, discovers possible bindings and toolchains, asks only for missing public inputs, writes values directly into `codepotg.yaml`, shows proposed dependency and command actions, and reports remaining manual steps.

## Commands and safety

Both project and pack manifests may declare structured before and after commands. Typed actions are preferred for dependency installation, formatting, linting, build runners, and validation. Raw commands remain available as structured executable plus arguments; shell strings are a separately controlled capability.

Local project commands are allowed by the normal trusted-project policy unless the project or host tightens it. Downloaded pack commands require approval by default. Server, playground, and MCP hosts deny commands by default. Host policy always wins. Approvals bind to the exact pack source, resolved commit, manifest digest, command identity, executable, arguments, working directory, and requested capabilities.
