# Complete linked project and pack example

This example shows how `codepotg.yaml` and `CodepotgPack.yaml` cooperate without exposing pack internals to the project.

## Project repository

```text
organiser/
├── codepotg.yaml
├── package.json
├── pnpm-lock.yaml
├── src/
└── _/
```

## Project `codepotg.yaml`

```yaml
apiVersion: codepotg.dev/v2
kind: Project

metadata:
  name: defytickets-organiser

allow: true

sources:
  backendApi:
    adapter: openapi
    path: ../backend/sdk/openapi/openapi.v1.yaml
    options:
      validation: strict

toolchains:
  node:
    version: ">=20"
    packageManager: pnpm

security:
  commands:
    project: allow
    packs: requireApproval
  dependencyLifecycleScripts: requireApproval

commands:
  before:
    - id: generate-openapi-spec
      name: Generate OpenAPI specification from backend contracts
      cwd: ../backend
      executable: pnpm
      arguments: [exec, codepot-openapi, generate]
  after: []

packs:
  serverSdk:
    use:
      github: alidantech-org/codepotg-next-actions-pack
      ref: v2.0.0
    source: backendApi
    profile: modular
    output:
      root: ./_
    clean:
      - gen
    options:
      generateExamples: false
      generateTests: true
    bindings:
      common:
        from:
          barrel: "@modules/common"
        symbols:
          logger: AppLogger
          tokenProvider: TokenProvider
      serverClient:
        symbol: ServerClient
        from:
          projectPath: src/lib/server-client.ts
    overrides:
      languages:
        typescript:
          imports:
            strategy: alias
            aliases:
              "@": ./src
              "@modules": ./src/modules
    commands:
      before: []
      after:
        - id: project-typecheck-generated
          executable: pnpm
          arguments: [typecheck:gen]
          optional: true
```

The project knows only:

- the source;
- the selected pack/profile;
- output and clean scope;
- public pack options;
- public bindings;
- permitted overrides;
- project-owned commands.

It does not list internal templates or select a language.

## Pack repository

```text
codepotg-next-actions-pack/
├── CodepotgPack.yaml
├── templates/
│   ├── models/
│   │   └── model.ts.jinja
│   ├── actions/
│   │   └── action.ts.jinja
│   ├── index.ts.jinja
│   ├── all.ts.jinja
│   ├── README.md.jinja
│   ├── eslint.config.mjs
│   ├── .gitignore
│   └── _partials/
│       └── license.txt.jinja
└── docs/
    ├── setup.md
    └── bindings/
        ├── logger.md
        ├── token-provider.md
        └── server-client.md
```

## Pack `CodepotgPack.yaml`

```yaml
apiVersion: codepotg.dev/v2
kind: TemplatePack

metadata:
  id: alidantech/next-actions
  version: 2.0.0
  description: Generates typed server actions and supporting SDK files.
  documentation: docs/setup.md

compatibility:
  codepotg: ">=2.0.0 <3.0.0"
  ir: ">=2.0 <3.0"

integration:
  createsProject: false
  ownsFolder: false
  contributesFiles: true
  requiresDependencies: true
  requiresBindings: true
  runnableAlone: false
  manifestMode: contribute

content:
  root: templates
  ignore:
    - "_authoring/**"
    - "**/*.draft"

writePolicy:
  defaultMode: managed
  managedRoots: [gen]

options:
  generateExamples:
    type: boolean
    default: false
    description: Generate example request usage.
  generateTests:
    type: boolean
    default: true
    description: Generate representative tests.

languages:
  typescript:
    naming:
      types: pascalCase
      values: camelCase
      files: kebabCase
    imports:
      strategy: relative
      omitExtensions: true
      typeImports: separate

  markdown:
    formatting:
      lineWidth: 100

templateEngines:
  jinja:
    undefinedBehavior: error
    whitespace:
      trimBlocks: true
      leftStripBlocks: true
      keepTrailingNewline: true

bindings:
  logger:
    kind: import
    target: typescript
    required: false
    title: Application logger
    acceptedSources: [module, projectPath, barrel]
    documentation: docs/bindings/logger.md
    whenMissing: omit

  tokenProvider:
    kind: import
    target: typescript
    required: false
    title: Authentication token provider
    acceptedSources: [module, projectPath, barrel]
    documentation: docs/bindings/token-provider.md
    whenMissing: omit

  serverClient:
    kind: import
    target: typescript
    required: true
    title: Project server client
    acceptedSources: [module, projectPath, barrel]
    documentation: docs/bindings/server-client.md
    whenMissing: prompt

selections:
  models:
    from: schemas.models
    as: model
    orderBy: name

  operations:
    from: operations
    as: operation
    orderBy: operationId

  completeSdk:
    scope: aggregate
    collect:
      models:
        from: schemas.models
        orderBy: name
      operations:
        from: operations
        orderBy: operationId

filePatterns:
  "models/**":
    output:
      root: gen/models

  "actions/**":
    output:
      root: gen/actions

files:
  "models/model.ts.jinja":
    id: model
    role: template
    selection:
      use: models
    output:
      path: gen/models/{model.fileName}.ts
    provides:
      - model.{model.id}

  "actions/action.ts.jinja":
    id: action
    role: template
    selection:
      use: operations
    uses:
      bindings: [logger, tokenProvider, serverClient]
    output:
      path: gen/actions/{operation.fileName}.ts
    provides:
      - action.{operation.id}

  "index.ts.jinja":
    id: index
    role: barrel
    selection:
      scope: aggregate
    exports:
      include: [model, action]
    output:
      path: gen/index.ts

  "all.ts.jinja":
    id: completeSdk
    role: template
    selection:
      use: completeSdk
    uses:
      bindings: [logger, tokenProvider, serverClient]
    output:
      path: gen/sdk.ts

  "README.md.jinja":
    id: generatedReadme
    role: template
    selection:
      scope: project
    output:
      path: gen/README.md

  "_partials/license.txt.jinja":
    id: licenseHeader
    role: partial
    target: plainText

  "eslint.config.mjs":
    id: eslintConfig
    role: static
    output:
      path: gen/eslint.config.mjs

  ".gitignore":
    id: generatedIgnore
    role: static
    output:
      path: gen/.gitignore

profiles:
  modular:
    enable: [model, action, index, generatedReadme, eslintConfig, generatedIgnore]

  monolithic:
    enable: [completeSdk, generatedReadme, eslintConfig, generatedIgnore]

dependencies:
  node:
    runtime:
      zod: "^4.0.0"
    development:
      eslint: "^9.0.0"
      prettier: "^3.0.0"
    packageManagers:
      supported: [npm, pnpm, yarn]

setup:
  summary: Configure project client imports and optional logging/authentication integrations.
  documentation: docs/setup.md
  questions:
    - binding: serverClient
      prompt: Select the project server client export.
    - binding: logger
      prompt: Select an application logger or omit logging.
    - binding: tokenProvider
      prompt: Select a token provider or omit authenticated requests.
  actions:
    after:
      - id: ensure-dependencies
        action: node.dependencies.ensure
        approval: required
  manualSteps:
    - id: expose-server-client
      title: Ensure the selected server client is available to generated actions.
      documentation: docs/bindings/server-client.md

commands:
  after:
    - id: remove-unused-imports
      action: node.eslint.fix
      paths: ["{output.root}/gen/**/*.{ts,tsx}"]
      optional: true

    - id: format-generated
      action: node.format
      paths: ["{output.root}/gen"]
      optional: true

overridePolicy:
  languages:
    typescript:
      imports:
        strategy: allow
        aliases: allow
        omitExtensions: allow
      naming:
        files: allow
  templateEngines:
    jinja:
      whitespace:
        trimBlocks: allow
        leftStripBlocks: allow
```

## Resolution summary

During planning:

1. `serverSdk` resolves the pack and source.
2. Every template's target is inferred from its filename.
3. The `modular` profile activates models, actions, authored barrel, docs, and static files.
4. Project bindings satisfy logical binding IDs; the TypeScript adapter calculates imports.
5. Pack dependencies become typed `package.json` contributions.
6. Pack actions/commands are shown for approval according to policy.
7. All outputs and graph dependencies are validated before rendering.
8. Templates/static files stage under `./_`.
9. Approved unused-import and formatting actions run in the declared phase.
10. The writer commits the complete validated result.

The project user never needs to know the pack's internal template paths.
