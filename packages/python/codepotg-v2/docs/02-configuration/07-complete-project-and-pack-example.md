# Complete linked project and pack example

This example shows how `codepotg.yaml`, `CodepotgPack.yaml`, and tokenized pack source paths cooperate without exposing pack internals to the project.

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

The project knows only the source, pack/profile, output and clean scope, public options, public bindings, permitted overrides, and project-owned commands. It does not list internal templates, output filenames, path recipes, or one global language.

## Pack repository

The path tokens are real pack source names:

```text
codepotg-next-actions-pack/
├── CodepotgPack.yaml
├── templates/
│   ├── {models}/
│   │   └── [model.name.kebab.s].model.ts.jinja
│   ├── {actions}/
│   │   └── [operation.name.kebab.o].action.ts.jinja
│   ├── {generatedRoot}/
│   │   ├── index.ts.jinja
│   │   ├── sdk.ts.jinja
│   │   ├── README.md.jinja
│   │   ├── eslint.config.mjs
│   │   └── .gitignore
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

paths:
  models:
    selection:
      use: models
    parts:
      - gen
      - models

  actions:
    selection:
      use: operations
    parts:
      - gen
      - actions

  generatedRoot:
    parts:
      - gen

filePatterns:
  "_partials/**/*.jinja":
    role: partial

  "**/*.spec.ts.jinja":
    profiles: [tests]

files:
  "{models}/[model.name.kebab.s].model.ts.jinja":
    id: model
    role: template
    provides:
      - model.semantic

  "{actions}/[operation.name.kebab.o].action.ts.jinja":
    id: action
    role: template
    uses:
      bindings: [logger, tokenProvider, serverClient]
    provides:
      - action.operation

  "{generatedRoot}/index.ts.jinja":
    id: index
    role: barrel
    selection:
      scope: aggregate
    exports:
      include: [model, action]

  "{generatedRoot}/sdk.ts.jinja":
    id: completeSdk
    role: template
    selection:
      use: completeSdk
    uses:
      bindings: [logger, tokenProvider, serverClient]

  "{generatedRoot}/README.md.jinja":
    id: generatedReadme
    role: template
    selection:
      scope: project

  "_partials/license.txt.jinja":
    id: licenseHeader
    role: partial
    target: plainText

  "{generatedRoot}/eslint.config.mjs":
    id: eslintConfig
    role: static

  "{generatedRoot}/.gitignore":
    id: generatedIgnore
    role: static

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
  templateEngines:
    jinja:
      whitespace:
        trimBlocks: allow
        leftStripBlocks: allow
```

## Destination examples

Given selected records named `Order`, `Orders`, and `ListOrders`, the source path rules may produce:

```text
{models}/[model.name.kebab.s].model.ts.jinja
→ gen/models/order.model.ts

{actions}/[operation.name.kebab.o].action.ts.jinja
→ gen/actions/list-orders.action.ts

{generatedRoot}/index.ts.jinja
→ gen/index.ts

{generatedRoot}/eslint.config.mjs
→ gen/eslint.config.mjs
```

The model name is deliberately singularized through `.s`; the operation name keeps its original lexical number through `.o`.

## Planning summary

1. `serverSdk` resolves the pack and semantic source.
2. The selected profile activates source descriptors.
3. Engine and target adapters are inferred from each source filename.
4. Named path recipes establish selections and output parts.
5. Dynamic name tokens apply explicit case and original/singular/plural projections.
6. Project bindings satisfy logical pack binding IDs.
7. The TypeScript adapter plans imports but does not plan output folders.
8. Dependencies become typed `package.json` contributions.
9. Commands/actions are inspected and approved according to policy.
10. Every output and graph edge is validated before rendering.
11. Files stage beneath the project pack-instance root `./_`.
12. The complete transaction commits only after validation succeeds.

The project user never needs to know the pack's internal source paths, but pack authors have full explicit control over path composition.
