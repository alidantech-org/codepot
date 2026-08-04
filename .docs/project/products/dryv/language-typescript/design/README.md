# TypeScript target adapter design reference

## Role

This package is resolved independently for every template whose target suffix is TypeScript. It detects and validates TypeScript targets and calculates target-aware module/path facts from already planned artifacts.

It never selects templates, extends the semantic kernel, assumes a framework, or authors TypeScript source text.

## Planned plugin entry point

```toml
[project.entry-points."dryv.language_adapters"]
typescript = "dryv_language_typescript.plugin:create_plugin"
```

## Target descriptors

```text
typescript: .ts, .mts, .cts
typescript-jsx: .tsx
```

The exact descriptor split is an implementation decision, but all targets use one package and compatible validation/path contracts. Longest-known suffix matching preserves names such as `types.d.ts.jinja` as `types.d.ts` output.

## Typed target options

Options are limited to target detection, filename/identifier validation, and module-path facts. A possible shape is:

```yaml
targets:
  typescript:
    files:
      declarationSuffix: .d.ts
    modules:
      strategy: relative
      aliases: {}
      omitExtensions: true
      indexResolution: omitIndex
    validation:
      reservedWordPolicy: diagnostic
```

Every option is implemented through typed immutable models, validation, descriptors, and introspection. Raw dictionaries and generic recursive merges are prohibited.

The adapter must not define options for generated type mapping, literal/comment style, import/export statement rendering, decorators, validators, formatting, semicolons, or framework conventions. Those are pack/template options and macros.

## Module/path facts

Given planned consumer/provider artifacts, the adapter may calculate and validate:

```text
relative path segments
normalized module specifier
alias match and remainder
package/module identity
extension omission or requirement
index resolution
path escaping/invalid target diagnostics
```

Example descriptor supplied to a template:

```text
module.symbols = [User]
module.specifier = @/types/user
module.is_relative = false
module.is_type_only = true     # semantic usage fact from the dependency request
```

The template authors the statement:

```jinja
import type { {{ module.symbols | join(", ") }} } from "{{ module.specifier }}";
```

The adapter does not return the rendered line and does not choose quote, semicolon, ordering, grouping, alias spelling, or statement form.

## Identifier and filename validation

Core supplies semantic naming projections in the fixed order:

```text
x.name.{casing}.{number}
```

Templates select the projection they want. The adapter may validate an authored candidate as a TypeScript identifier, property name, namespace, file stem, or reserved word and return diagnostics/facts. It does not expose alternate APIs such as `typescript.className` or rename semantic objects automatically.

## Internal implementation shape

```text
TypeScriptTargetAdapter
├── TargetDescriptorRegistry
├── FileNameValidator
├── IdentifierValidator
├── ReservedWordCatalog
├── ModulePathResolver
├── ModuleSpecifierValidator
└── CapabilityDescriptor
```

No type renderer, literal renderer, comment renderer, import renderer, or export renderer belongs in this package.

## Boundaries

This package contains no:

- semantic source parsing;
- semantic object/facet/selector registration;
- generated type/literal/comment/import/export/decorator/validator syntax;
- Node package-manager or `package.json` modification;
- NestJS/Next.js/React rules;
- Jinja rendering;
- template selection;
- destination planning or writing;
- command execution;
- old generator imports.

See the detailed task ledger in `../tasks/00-package-plan.md` and the core contract in `dryv/docs/04-plugins/02-language-adapter-contract.md`.
