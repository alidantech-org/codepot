---
title: Package configuration
description: Configure contracts, output files, servers, compilation, validation, and logging.
product: codepot-openapi
package: codepot-openapi
order: 4
---

# Package configuration

A contract file exports the result of `definePackageConfig`.

```ts
export default definePackageConfig({
  contracts: [v1, v2],
  output: {
    folder: 'openapi',
    filePrefix: 'service',
    formats: ['json', 'yaml'],
    debugFilePrefix: 'debug',
  },
  server: {
    url: 'https://api.example.com',
    description: 'Production API',
  },
  validation: {
    enabled: true,
    failOnWarnings: false,
    allowUnusedComponents: false,
  },
  logging: {
    level: 'info',
  },
});
```

## `contracts`

`contracts` is the required ordered list of version builders. Each builder compiles to its own OpenAPI document and output file set.

Keep version contracts independent. Share reusable TypeScript helpers where useful, but avoid mutating one version from another.

## `output`

| Field | Meaning |
|---|---|
| `folder` | Output directory relative to the working directory |
| `filePrefix` | Base file name used for generated documents |
| `formats` | Any ordered combination of `json` and `yaml` |
| `debugFilePrefix` | Optional prefix for compiler debug output |

The exported `PackageOutputFormat` values are `json` and `yaml`.

## `server`

The optional package server adds a server URL and description to generated documents when the contract does not provide more specific server behavior.

```ts
server: {
  url: 'http://localhost:5000',
  description: 'Local development',
}
```

## `compile`

`compile` accepts `CompileOptions`. Use it for compiler-level behavior rather than output formatting. Prefer defaults unless a project has a documented reason to change a compiler option.

## `validation`

| Field | Default intent |
|---|---|
| `enabled` | Run generated-document validation |
| `failOnWarnings` | Treat warnings as a failed generation |
| `allowUnusedComponents` | Permit reusable components that are not referenced by a route |

Warnings are useful during contract development. Production release checks can enable stricter behavior.

## `logging`

Logging configuration controls compiler and CLI diagnostics. It does not change the generated contract.

## Configuration resolution

`resolvePackageConfig`, `resolveOutputConfig`, and `resolveCompileOptions` expose the normalized forms used internally. Most projects should call `definePackageConfig` and let the CLI resolve defaults.

## Recommended layout

```text
project/
├── codepot-openapi.config.ts
├── src/
│   └── contracts/
│       ├── shared.ts
│       ├── users.ts
│       └── orders.ts
└── openapi/
    ├── service-v1.json
    └── service-v1.yaml
```

The root config can import contract modules while remaining the single package entry point.