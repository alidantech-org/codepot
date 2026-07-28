# Language and target-syntax adapter contract

## Responsibility

A language adapter describes and validates one target syntax for already authored template files. It is resolved independently for every template from the detected target suffix.

A project and pack may use many target adapters in one generation run.

A language adapter is not a code renderer. Templates, macros, partials, and static files own every emitted character.

## Installable package

A language adapter is an ordinary independently versioned Python distribution, for example:

```text
dryv-language-typescript
dryv-language-dart
dryv-language-python
```

It registers a factory through `dryv.language_adapters`.

## Target descriptor

The adapter declares one or more target descriptors:

```text
id
aliases
file extensions
syntax category
filename/reserved-name validation behavior
module/path capability facts
supported validation capabilities
behavior version
```

Syntax categories may include programming language, markup, data, configuration, query language, and plain text.

Extension resolution uses longest-known matching. Removing the engine suffix never changes the intended output suffix.

## Required services

A target adapter may implement applicable services for:

- target extension registration and inference;
- target filename/stem validation;
- reserved filename and identifier diagnostics;
- optional validation/escaping facts for explicitly supplied candidate identifiers;
- destination-relative module/path normalization;
- target-specific module specifier validation;
- index/module extension conventions needed to calculate path facts;
- package/module/namespace path validation for project bindings;
- target capability reporting;
- deterministic validation and behavior introspection.

The adapter returns typed facts and diagnostics. It does not return source-code snippets or statements.

## Prohibited syntax services

A language adapter must not render or inject:

- primitive or composite type syntax;
- optional/nullable syntax;
- generics, unions, intersections, functions, records, arrays, or maps;
- enum declarations;
- literals or escaping syntax for emitted source;
- comments or documentation comments;
- import statements;
- export statements;
- decorators, annotations, attributes, validators, modifiers, or framework calls;
- class, interface, type, struct, record, trait, repository, controller, widget, or entity syntax;
- formatting, semicolons, quotes, indentation, or textual ordering.

Those are pack/template concerns.

A target adapter may validate a path/module specifier or candidate identifier and expose safe normalized facts. The template decides how to spell and position those facts.

## Naming boundary

Core owns semantic name projections:

```text
x.name.{casing}.{number}
```

Language adapters do not create alternate naming APIs such as `language.className`, `language.fieldName`, or `language.fileName`.

Templates may select the documented core projection they want and may use pack-authored macros for additional output conventions.

## Module/path contract

Core plans source and destination artifacts. A target adapter may calculate or validate target-aware module/path facts from already planned destinations and project bindings.

A module descriptor may expose facts such as:

```text
provider artifact identity
consumer artifact identity
relative path segments
normalized module specifier
requires extension
resolves through index
package/module identity
validation diagnostics
```

The template authors the import/export statement:

```jinja
{% for module in imports.schemaType.modules %}
import type { {{ module.symbols | join(", ") }} } from "{{ module.specifier }}";
{% endfor %}
```

The adapter must not supply a pre-rendered statement.

## Target options and rules

Any target configuration must be limited to facts required for detection, path calculation, validation, or capability reporting.

Possible typed sections include:

```yaml
targets:
  typescript:
    files: {}
    modules: {}
    validation: {}
```

Do not add language rule sections for generated type mapping, literal rendering, comment style, imports, exports, decorators, or formatting. Those belong in pack options and templates when variability is needed.

Raw mappings and generic recursive merges are prohibited. Every supported option is typed, documented, introspectable, and behavior-versioned.

## Capabilities

Capabilities describe validation/path support rather than generated syntax. Examples may include:

```text
file.extension.ts
file.extension.tsx
file.declaration_name
module.relative_path
module.package_path
module.index_resolution
module.extension_policy
identifier.validate.type
identifier.validate.value
identifier.reserved_words
```

A capability does not authorize the adapter to emit code.

## Context safety

The adapter receives immutable planned artifact/path descriptors and the minimum target configuration required for its service. It must not mutate semantic IR, selections, invocations, artifacts, or pack files.

It does not receive authority to add template-context properties outside the documented target/path descriptor contract.

## Prohibited responsibilities

A language adapter must not:

- parse OpenAPI or other semantic sources;
- extend the semantic kernel or register facets/selectors;
- select records or templates;
- discover packs;
- render Jinja or another engine;
- render source-code syntax;
- write output files;
- execute commands;
- own cache persistence;
- inspect CLI arguments;
- encode framework architecture;
- assume TypeScript means Node/NestJS/Next.js or Dart means Flutter.

## Factory example

```python
def create_plugin() -> LanguageAdapterPlugin:
    return LanguageAdapterPlugin(
        id="typescript",
        version="1.0.0",
        api_version="1",
        core_versions=">=2,<3",
        targets=(typescript_descriptor,),
        option_schema=typescript_target_option_schema,
        factory=TypeScriptTargetAdapter,
    )
```

## Conformance tests

Every target package must run tests for:

- deterministic target/extension inference;
- longest-known extension matching;
- filename and reserved-name validation;
- candidate identifier validation where declared;
- relative destination/module path calculation;
- package/project-path binding validation;
- index and extension module-specifier behavior;
- typed option decoding and introspection;
- no emitted syntax or pre-rendered snippets;
- no semantic-kernel extension;
- immutable inputs;
- thread/session isolation;
- plugin descriptor compatibility.

Language-specific packages add focused tests only for their supported detection, filename, identifier-validation, and path/module facts.
