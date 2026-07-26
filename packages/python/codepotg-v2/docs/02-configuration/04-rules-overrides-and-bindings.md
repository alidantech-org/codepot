# Rules, overrides, and bindings

## Core-owned protocol

CodepotG core owns how rules are declared, decoded, merged, restricted, inspected, and documented. Language adapters, template-engine adapters, ecosystem adapters, and packs provide typed rule models within that protocol.

No implementation may deep-merge arbitrary dictionaries.

## Rule field metadata

Every rule field declares:

```text
path
value type
default
merge policy
override capability
security classification
documentation
examples
introduced version
```

Supported merge policies:

- `replace`;
- `append`;
- `prepend`;
- `union`;
- `mergeByKey`;
- `remove`;
- `resetToDefault`;
- `notOverridable`.

A patch distinguishes:

- not specified;
- set to value;
- remove;
- reset to adapter default.

`null` must not ambiguously mean all four states.

## Deterministic precedence

Effective rules are produced in this order:

1. adapter defaults;
2. pack rules;
3. exact template-local rules;
4. project global target or engine overrides;
5. project pack-instance overrides;
6. project template-specific overrides.

Every merge produces provenance so `codepotg inspect rules` can explain the origin of the final value.

## Restriction hierarchy

The effective permission is the strictest of:

1. host policy;
2. adapter hard restriction;
3. pack override policy;
4. project request.

A lower layer may tighten a rule but cannot loosen an upper restriction.

## Language rule families

Language adapters should organize applicable fields under stable families:

```text
identifiers
naming
files
modules
imports
exports
types
literals
comments
documentation
formatting
```

A language does not need to implement meaningless fields. Its descriptor states supported capabilities and fields. Unknown fields are errors.

## Template-engine rule families

Template-engine adapters should organize applicable fields under:

```text
undefined behavior
whitespace
includes and inheritance
sandbox
context access
filters and tests
render limits
output blocks
```

Security-sensitive fields such as Python builtin access, arbitrary imports, absolute filesystem access, and unrestricted attribute access are host-controlled and cannot be enabled by downloaded packs.

## Bindings

Bindings are pack-declared public integration points satisfied by a project pack instance.

The pack catalog defines:

- stable binding ID;
- kind;
- required or optional state;
- target syntax when applicable;
- expected symbol kind;
- accepted value sources;
- discovery hints;
- missing-value policy;
- documentation and examples.

Individual templates list the binding IDs they consume.

## Standard binding kinds

### `import`

Logical symbol import rendered by the target-language adapter.

### `barrel`

A project module/package entry point exporting one or more logical symbols.

### `projectPath`

Real project file path. The language adapter calculates a correct relative or configured module path from each output artifact.

### `package`

Package or namespace import such as Dart `package:` or Java package paths.

### `namespace`

Namespace import or language-specific module namespace.

### `text` and `textFile`

Controlled text values or declared project files exposed as immutable content.

### `value`

Typed scalar or structured configuration value.

### `packageName`

Project package identity used for package imports or manifests.

### `artifact`

Reference to a generated artifact or capability provided by another template or pack.

## Import sources

A TypeScript import binding may be configured as:

```yaml
symbol: BaseRepository
from:
  module: "@modules/common/base"
```

or:

```yaml
symbol: BaseRepository
from:
  projectPath: src/modules/common/base-repository.ts
```

or through a barrel group:

```yaml
from:
  barrel: "@modules/common"
symbols:
  baseRepository: BaseRepository
  logger: AppLogger
```

The adapter owns rendering, aliasing, extension omission, relative path calculation, deduplication, collision aliases, and import ordering.

## Raw escape hatch

A raw import or raw text binding may be supported for unusual syntax, but it must produce a warning that CodepotG cannot safely relocate, deduplicate, or semantically validate it.

Raw values must never become an implicit shell or Python execution path.

## Missing binding behavior

Per binding or project policy may select:

- `prompt`;
- `placeholder`;
- `omit` for optional behavior;
- `skipTemplate`;
- `error`.

Placeholders must be obvious and machine-detectable. Generation results list every unresolved binding and affected artifact.

Strict CI mode converts configured unresolved conditions into errors without removing flexible local generation.

## Discovery

A pack may provide hints such as:

- expected symbol names;
- file patterns;
- module alias patterns;
- project manifest keys;
- known framework locations.

`codepotg configure` may offer detected candidates but must not silently choose among ambiguous matches.

## Tests

Required contract tests cover:

- each merge policy;
- permission hierarchy;
- provenance of effective values;
- default barrel deduplication;
- relative path calculation;
- alias conflicts;
- missing binding policies;
- raw escape warnings;
- exact template-to-binding dependency mapping.
