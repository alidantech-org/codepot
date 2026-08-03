---
title: Generation, validation, and CLI
description: Compile contracts, validate output, write files, and use the command-line or programmatic APIs.
product: codepot-openapi
package: codepot-openapi
order: 10
---

# Generation, validation, and CLI

## CLI commands

```bash
codepot-openapi init
codepot-openapi generate
codepot-openapi validate
```

Use `npx codepot-openapi ...` when the package is installed locally and no package-manager script wraps the command.

## `init`

`init` creates a starter contract configuration. It is intended to establish file shape and package wiring, not to infer an application's domain model.

Review and replace example resources before generating a production contract.

## `generate`

`generate` performs the complete pipeline:

```text
load TypeScript config
    ↓ resolve package configuration
execute contract builders
    ↓ validate registries and references
compile each version
    ↓ validate OpenAPI document
serialize configured formats
    ↓ write deterministic files
report diagnostics and output paths
```

Generation fails when required references, routes, metadata targets, or document validation rules are invalid.

## `validate`

`validate` runs contract and OpenAPI validation without treating file output as the primary action. Use it in local checks and release validation.

Configuration controls:

- whether generated-document validation is enabled;
- whether warnings fail;
- whether unused components are allowed.

## Programmatic compiler

```ts
import { compileOpenApi } from 'codepot-openapi';

const result = compileOpenApi(versionContract, options);

if (!result.success) {
  for (const issue of result.issues) {
    console.error(issue.code, issue.message);
  }
  process.exitCode = 1;
} else {
  console.log(result.document);
}
```

`CompileResult` is a success/failure union. Check its discriminator before reading the compiled document.

## Programmatic generation

```ts
import { generateOpenApi } from 'codepot-openapi';
```

`generateOpenApi` combines package configuration, compilation, validation, and output writing. Its result reports generated files and diagnostics.

## File writing

```ts
import { writeOpenApiFiles } from 'codepot-openapi';
```

Use `writeOpenApiFiles` only when another tool already owns a compiled document and explicitly wants the package's output naming and serialization behavior.

## Document validation

```ts
import { validateOpenApiDocument } from 'codepot-openapi';
```

Document validation checks the emitted plain OpenAPI object. It is separate from builder validation because a contract can be internally resolvable yet still violate an OpenAPI rule or project validation policy.

## Logging

`CompilerLogger` supports package logging levels and structured compiler progress. Libraries embedding the compiler should avoid parsing CLI text; use programmatic results and logger configuration instead.

## Release checks

From the package directory:

```bash
pnpm typecheck
pnpm build
pnpm pack:dry
```

The dry pack verifies the published file set, ESM/CommonJS entrypoints, and declaration output.

## Troubleshooting

### Config cannot be loaded

- Confirm the file is named and located where the CLI expects it.
- Confirm the default export is the result of `definePackageConfig`.
- Confirm imported TypeScript modules are available from the project.

### A reference cannot be resolved

- Check registry ownership and exact names.
- Ensure a resource does not refer to a component from an unrelated version builder.
- Prefer returned ref objects over manually written `$ref` strings.

### OpenAPI validation fails

- Read the document-level issue path.
- Check duplicate operations, invalid path parameters, missing responses, and unsupported schema combinations.
- Inspect the generated JSON before changing templates or downstream generators.