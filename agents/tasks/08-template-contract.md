# Phase 08 — Template variable contract and validation

Status: [x]
Issue: #10
Depends on: completed authoring and templating engines
Commits: `a48797c7` through `17f0295b`
Validation: strict synthetic TypeScript check passed for the contract, context, catalog, AST inspection, templating engine, and runtime operation model. Focused repository tests cover catalog paths, aliases, arrays, requirements, helpers, partials, Markdown output, CLI request mapping, and rejection of unknown variables before render. Installed workspace execution remains in Phase 11 because the current environment cannot resolve npm or GitHub.

## Goal

Make every value available to Handlebars explicit, typed, listable, and validatable. Template authors must be able to inspect the complete context contract before writing a template, and Codepot must detect unknown or unavailable variables before rendering.

## Completed

- [x] Defined the versioned JSON-safe `TemplateVariableCatalog` artifact.
- [x] Added variable kinds, scopes, origins, requirements, examples, helper descriptors, partial descriptors, and Handlebars data variables.
- [x] Added typed requests/results and a dedicated `TemplateIntrospectionPort`.
- [x] Added deterministic context enrichment inspired by the Python `NameSet` and classified context contract.
- [x] Added Handlebars AST parsing without template execution.
- [x] Added variable, helper, partial, block-parameter, and `@data` reference collection.
- [x] Added context, requirement, selector, and dynamic output-path validation.
- [x] Added partial discovery and registration, hidden-file support, raw files, ignore rules, and safe helper registration.
- [x] Added `templating.variables` and `templating.context.validate` runtime operations.
- [x] Added `codepotx variables [task]` with Markdown and JSON output.
- [x] Added focused core and CLI tests.

## Preserved rules

- The catalog is serializable and contains no Zod or Handlebars runtime objects.
- Template validation does not execute templates.
- Unknown variables are errors in strict mode.
- Helpers, partials, block parameters, and `@data` values are separate namespaces.
- Templating consumes only stable artifacts and injected platform ports.
