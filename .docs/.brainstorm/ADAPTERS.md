Yes, **it may be possible to remove full language adapters entirely**, and your original instinct may produce a cleaner Dryv design.

The key question is:

> Does Dryv need to understand target-language semantics, or does it only need to provide enough planned information for templates to render them?

My assessment is that **full language adapters are probably unnecessary for Dryv’s core goals**.

# What templates already know

A template pack already knows:

* what language or file format it generates;
* how imports look;
* how exports look;
* how symbols are named;
* whether paths use `/`, `.`, `::`, or another separator;
* whether extensions are included;
* how aliases and package imports work;
* how reserved words should be escaped;
* how types should be rendered.

A TypeScript template author knows TypeScript better than Dryv core should.

For example, Dryv can expose:

```text
provider.symbol
provider.output.path
consumer.output.path
provider.output.directory
provider.output.filename
provider.output.extension
provider.semantic_id
provider.template_id
```

The template can then decide:

```jinja
import { {{ dependency.symbol }} }
from "{{ dependency.output.relative_to(output).without_extension | join_slash }}";
```

Or for Java:

```jinja
import {{ dependency.output.package_parts | join_dot }}.{{ dependency.symbol }};
```

Or Rust:

```jinja
use {{ dependency.output.module_parts | join_double_colon }}::{{ dependency.symbol }};
```

This keeps target syntax inside the pack.

# What Dryv should resolve

Dryv should still resolve the difficult semantic parts:

```text
Which authored item is needed?
Which template invocation provides it?
Which output artifact contains it?
Which symbol does that artifact expose?
What is the relationship between the consumer and provider?
```

Dryv should provide structured facts, not a rendered import statement.

For example:

```text
Resolved dependency
├── provider template
├── provider invocation
├── provider artifact
├── semantic subject
├── symbol name
├── output path
├── consumer path
├── common output root
└── relative path segments
```

The template then formats those facts.

This is an important boundary:

```text
Dryv resolves meaning and artifacts.
Templates render language syntax.
```

# Symbols should be template-owned declarations

A template can declare what symbols it emits.

Example concept:

```yaml
emits:
  symbols:
    - name: "{schema.name.pascal}"
      kind: type
      subject: schema
```

Dryv evaluates that declaration for each invocation and registers:

```text
Artifact:
  generated/models/user.ts

Emitted symbol:
  User

Semantic subject:
  schema users.User
```

A consumer template can declare that it needs the symbol emitted by another template:

```yaml
uses:
  symbols:
    - from: model
      subject: operation.output.schema
```

Dryv resolves the correct provider and exposes it to the template.

The template writes the import.

# This removes major adapter complexity

Removing full language adapters avoids:

* language plugin discovery;
* adapter compatibility versions;
* adapter configuration schemas;
* adapter-specific import planners;
* adapter-specific symbol renderers;
* adapter-specific type renderers;
* adapter-specific rule merging;
* framework-versus-language confusion;
* requiring an installed adapter for every file syntax;
* core logic branching around languages.

It also preserves the design principle that packs are powerful and portable.

# What still needs some language awareness

There are a few things Dryv may still benefit from knowing.

## 1. File extension recognition

Dryv needs to understand:

```text
.ts.jinja
.dart.jinja
.java.jinja
.yaml.jinja
```

But this can be a lightweight **target syntax registry**, not an adapter.

A descriptor might contain only:

```text
id
known extensions
category
known reserved words
optional filename rules
```

For example:

```text
typescript
  extensions: .ts, .tsx, .mts, .cts
  reserved words: class, function, import, export...
```

No rendering behavior is required.

## 2. Reserved-word warnings

Dryv can warn:

```text
Generated symbol 'class' is reserved in TypeScript.
```

But it should not necessarily decide how to fix it.

The pack may define:

```yaml
symbols:
  reservedWords:
    strategy: prefix
    value: "_"
```

Or handle it directly in a template helper:

```jinja
{{ schema.name.pascal | escape_reserved(keywords) }}
```

## 3. Unknown target syntax

A pack may generate a target Dryv does not recognize.

It should be allowed to provide its own metadata:

```yaml
targets:
  customLang:
    extensions:
      - .abc

    keywords:
      - module
      - type
      - import
```

Dryv can then perform basic warnings without needing a Python plugin.

This is much more portable than requiring a separately installed language adapter.

# Keyword lists should belong to packs or reusable data packages

Your keyword idea is practical.

There could be three sources of keyword knowledge:

```text
Dryv built-in common registry
Pack-provided additions
Project overrides
```

Precedence could be:

```text
Known target defaults
→ pack target configuration
→ project target overrides
```

But this should remain data, not executable adapters.

Example:

```yaml
targets:
  typescript:
    keywords:
      include:
        - satisfies
        - infer

      symbolPolicy:
        reserved: warn
```

For an unknown language:

```yaml
targets:
  codepot:
    extensions:
      - .codepot

    keywords:
      - module
      - resource
      - schema
      - operation
```

# Path helpers are likely enough

Dryv can expose generic path values:

```text
path.parts
path.directory_parts
path.filename
path.stem
path.extensions
path.relative_parts
path.absolute_within_output
```

Template engines can provide generic helpers:

```text
join_slash
join_dot
join_double_colon
join_backslash
remove_extension
replace_extension
parent
relative_to
normalize
```

Examples:

```jinja
{{ dependency.path.relative_parts | join_slash }}
```

```jinja
{{ dependency.path.relative_parts | join_dot }}
```

```jinja
{{ dependency.path.relative_parts | join_double_colon }}
```

These are not language adapters. They are normal template utilities.

# Type rendering is the harder question

Imports are easy to leave to templates.

Types are more complicated.

Suppose Runtime IR exposes:

```text
array<string>
optional<User>
map<string, integer>
union<User, Admin>
```

Different languages render these differently:

```text
TypeScript:
User[]
User | undefined
Record<string, number>

Dart:
List<String>
User?
Map<String, int>

Rust:
Vec<String>
Option<User>
HashMap<String, i64>
```

There are three possible designs.

## Option A — Templates render all types

Dryv exposes the typed IR structure:

```text
type.kind
type.item
type.key
type.value
type.members
type.nullable
type.reference
```

Templates recursively render it.

Advantages:

* No language adapters
* Maximum pack control
* No hidden rendering
* Framework-specific type rules remain pack-owned

Risks:

* Type-rendering logic may be repeated across templates
* Pack authors need reusable macros/helpers
* Complex recursion can make templates harder to maintain

This can be reduced through pack-owned macros:

```text
helpers/types.ts.jinja
helpers/types.dart.jinja
```

## Option B — Declarative target rules

A pack defines type-rendering patterns as data.

Example concept:

```yaml
targets:
  typescript:
    types:
      string: string
      integer: number
      array: "{item}[]"
      nullable: "{value} | null"
```

Advantages:

* Still no executable adapters
* Reusable across templates
* Easy to inspect

Risks:

* A miniature rendering language may emerge
* Advanced language types may exceed declarative rules
* Could become more complex than template macros

## Option C — Optional helper plugins

Core does not require language adapters.

A pack may optionally use a helper plugin that provides convenience functions:

```jinja
{{ types.render(field.type) }}
```

The plugin does not own planning, imports, outputs, or semantics.

Advantages:

* Complex packs can reuse mature helpers
* Simple packs remain dependency-free
* No mandatory language architecture

Risks:

* Reintroduces executable plugin complexity
* Pack portability depends on installed helpers
* Needs clear trust and compatibility rules

# My recommendation

The cleanest direction is:

```text
No mandatory language adapters.
```

Use:

1. **Template-owned symbols**
2. **Dryv-resolved artifact relationships**
3. **Generic path tokens**
4. **Generic path and naming helpers**
5. **A lightweight declarative target registry**
6. **Pack-provided keyword lists**
7. **Pack-owned type-rendering macros**
8. **Optional helper plugins only when a pack explicitly needs them**

This preserves maximum pack power without forcing every language through a central abstraction.

# Suggested responsibility boundary

Dryv should know:

```text
Semantic identities
Template invocations
Artifact identities
Output paths
Emitted symbols
Requested symbols
Provider/consumer relationships
Relative path facts
Dependency ordering
```

Dryv should not know:

```text
How to spell an import
How to spell an export
How to render a type
How to escape an identifier
How to declare a class
How to write framework syntax
```

Those belong to templates and pack helpers.

# Main risk of removing language adapters

The biggest risk is duplicated pack logic.

Ten TypeScript packs might each implement:

* type rendering;
* reserved-word escaping;
* path conversion;
* import formatting;
* documentation comments.

But duplication can be addressed through reusable pack components or helper libraries without making them part of Dryv core.

For example, a pack could depend on:

```text
dryv-pack-helpers-typescript
```

That dependency could provide:

* Jinja macros
* keyword data
* naming filters
* type-rendering fragments

It remains pack-level composition, not a runtime language adapter.

# Human decision checklist

## Decision: Mandatory language adapters

Status: **UNDER REVIEW**

Proposal:

```text
Remove mandatory language adapters from the Dryv architecture.
```

## Decision: Responsibility for import syntax

Status: **PROPOSED**

Proposal:

```text
Dryv resolves provider artifacts and path facts.
Templates render import syntax.
```

## Decision: Symbol ownership

Status: **PROPOSED**

Proposal:

```text
Templates declare emitted symbols.
Dryv registers and resolves them semantically.
```

## Decision: Target-language awareness

Status: **PROPOSED**

Proposal:

```text
Use lightweight declarative target descriptors rather than executable language adapters.
```

## Decision: Reserved words

Status: **PROPOSED**

Proposal:

```text
Dryv and packs maintain keyword lists for validation and warnings.
Packs decide how identifiers are escaped or renamed.
```

## Decision: Type rendering

Status: **UNREVIEWED**

Options:

```text
A. Fully template-owned macros
B. Declarative target type rules
C. Optional helper plugins
D. A controlled combination
```

My assessment is that your original preference is architecturally viable and likely simpler:

> **Dryv should resolve semantic relationships and artifact paths, while smart templates remain responsible for target-language syntax.**

You are right. We should assess **complete elimination**, not preserve language adapters under another name.

## Conclusion

**Yes, Dryv can eliminate language adapters entirely.**

Once Dryv already understands:

* semantic subjects;
* templates;
* template invocations;
* generated artifacts;
* emitted symbols;
* consumed symbols;
* output paths;
* relative path facts;
* provider and consumer relationships;

a language adapter becomes an unnecessary second owner of generation behavior.

That would create two competing authorities:

```text
Template pack decides generated syntax
Language adapter also decides generated syntax
```

One of them must go.

Dryv’s original goal gives the stronger answer:

> **Templates and packs own generated language syntax. Dryv owns semantic planning and artifact relationships.**

Therefore language adapters should be removed from the architecture.

# What Dryv should understand

Dryv should understand only neutral generation facts:

```text
Authored semantic item
Template selected for that item
Template invocation
Output artifact
Emitted symbol
Required symbol
Provider artifact
Consumer artifact
Output path
Relative path between artifacts
Generation dependency
```

Example resolved facts:

```text
Consumer:
  template: service
  output: src/services/user.service.ts

Required symbol:
  User

Provider:
  template: model
  output: src/models/user.ts

Relative path parts:
  ../models/user
```

Dryv stops there.

The template decides how to render it:

```jinja
import { {{ dependency.symbol }} }
from "{{ dependency.relative_path | join_slash }}";
```

Another pack can render the same path facts differently:

```jinja
import {{ dependency.path_parts | join_dot }}.{{ dependency.symbol }};
```

Or:

```jinja
use {{ dependency.path_parts | join_double_colon }}::{{ dependency.symbol }};
```

No language-specific runtime component is needed.

# What templates and packs own

Templates and their helpers own:

* import syntax;
* export syntax;
* type syntax;
* class and function syntax;
* comments;
* annotations and decorators;
* literal formatting;
* identifier formatting;
* reserved-word handling;
* module syntax;
* package syntax;
* file naming;
* framework conventions;
* extension handling;
* language-specific validation commands.

Dryv should not try to understand or reproduce those rules.

# Symbols replace the main reason for adapters

Language adapters were previously proposed mainly to solve:

* imports;
* symbols;
* paths;
* type rendering;
* naming;
* reserved words.

But explicit symbols and artifact relationships already solve the difficult part.

A template declares what it emits:

```yaml
symbols:
  - name: "{schema.name.pascal}"
    subject: schema
    purpose: model
```

A consuming template declares what it needs:

```yaml
uses:
  symbols:
    - subject: operation.output.schema
      purpose: model
```

Dryv resolves:

```text
semantic subject
→ providing template invocation
→ artifact
→ symbol
→ path relationship
```

The template renders the import.

The adapter would merely format information that the template already needs and already controls.

# Type rendering also belongs to templates

Dryv exposes neutral type structure:

```text
field.type.kind
field.type.item
field.type.key
field.type.value
field.type.members
field.type.reference
field.required
field.nullable
```

The pack renders it using templates or macros.

For TypeScript:

```jinja
{% macro render_type(type) %}
...
{% endmacro %}
```

For Dart:

```jinja
{% macro render_type(type) %}
...
{% endmacro %}
```

For Java:

```jinja
{% macro render_type(type) %}
...
{% endmacro %}
```

Reusable language logic can be shared through:

* pack dependencies;
* shared template fragments;
* macros;
* helper files;
* reusable pack libraries.

That reuse remains in the templating tier rather than creating another generation authority.

# Keywords do not require adapters

Reserved words can be ordinary pack data.

```yaml
targets:
  typescript:
    keywords:
      - class
      - function
      - import
      - export
```

Or the pack can load a reusable keyword file:

```yaml
keywords:
  file: helpers/typescript-keywords.txt
```

For an uncommon or private language, the pack supplies its own list.

Dryv may:

* expose the list to templates;
* warn when a declared symbol matches a listed keyword;
* show the warning in the plan.

Dryv should not decide how to rename or escape the symbol. The template pack decides that.

A pack may define:

```jinja
{{ symbol.name | safe_identifier(keywords, prefix="_") }}
```

Or handle it through an authored macro.

# Target language can be opaque metadata

Dryv does not need a language registry.

A template may have a target label inferred from its filename:

```text
model.ts.jinja
```

or explicitly declared:

```yaml
target: typescript
```

Dryv treats `typescript` as an opaque pack-defined identifier.

It may use the target label for:

* diagnostics;
* grouping;
* compatibility declarations;
* plan inspection;
* warning about suspicious cross-target dependencies.

It does not need to know TypeScript syntax.

A private language works immediately:

```yaml
target: company-language
```

No runtime extension is required.

# Cross-target relationships

Dryv should not automatically decide that two targets are compatible.

The pack declares compatibility when needed:

```yaml
targetCompatibility:
  typescript:
    canReference:
      - typescript
      - javascript
```

Or a template can explicitly allow a dependency.

Without a declaration, Dryv can warn:

```text
Template target 'typescript' consumes a symbol emitted by target 'dart'.
```

Again, this is pack data, not executable language behavior.

# Project overrides remain pack-owned

A project may want:

```text
TypeScript imports through @/
Dart package imports
Java package names
Rust crate paths
```

Those become pack options or bindings:

```yaml
packs:
  backend:
    options:
      importStyle: alias
      importPrefix: "@/"
```

The pack defines what those options mean.

Dryv validates them against the pack’s declared option schema but does not interpret them as universal language rules.

This prevents Dryv from accumulating a large global language-configuration system.

# What is lost by removing adapters

We lose centralized automatic handling of:

* target-language type rendering;
* import formatting;
* reserved-word escaping;
* identifier validation;
* language-wide defaults.

But that centralization is not necessarily desirable.

It would:

* constrain powerful templates;
* duplicate pack logic;
* create plugin compatibility problems;
* make uncommon languages harder to support;
* mix templating responsibilities into runtime extensions;
* make packs less self-contained;
* introduce hidden behavior outside the pack.

Dryv can still provide generic, non-language-specific helpers:

```text
join_slash
join_dot
join_colon
relative_path
without_extension
replace_extension
parent_path
name casing
deduplicate
sort
```

These helpers manipulate neutral values. They do not understand a programming language.

# Validation after removing adapters

Dryv validates generation structure:

* symbols are declared;
* symbol providers exist;
* providers are unambiguous;
* paths are valid;
* dependencies are resolvable;
* output collisions do not exist;
* template contexts are valid;
* templates only use available variables;
* artifact cycles are explained;
* bindings are satisfied according to pack policy.

Target-language correctness is validated by the pack’s own tools:

* compiler;
* formatter;
* linter;
* type checker;
* parser;
* test command.

This is appropriate because the pack knows which tools and rules apply.

# Clean final boundary

```text
Dryv owns:
  semantic IR
  selection
  template invocations
  artifacts
  symbols
  dependencies
  paths
  bindings
  planning
  tracing
  output safety

Template packs own:
  language syntax
  type rendering
  imports and exports
  identifier rules
  reserved words
  framework rules
  formatting
  target validation
```

## Checklist update

### Mandatory language adapters

**Status: REJECTED**

Approved direction from your correction:

> Dryv should not require or retain language adapters.

### Language-specific generation behavior

**Status: UNDER REVIEW**

Current direction:

> Language-specific behavior belongs to templates, pack helpers, pack data, and pack configuration.

### Symbol and path resolution

**Status: UNDER REVIEW**

Current direction:

> Dryv resolves semantic symbols, artifacts, and path facts; templates render the final target syntax.

### Keywords

**Status: UNDER REVIEW**

Current direction:

> Keyword lists are declarative pack data used for warnings and template-controlled identifier handling.

The architecture is cleaner if language adapters are eliminated completely rather than weakened, renamed, or made optional.

Yes. This can be handled efficiently without language adapters.

The key is to treat a barrel as a normal generated artifact that **re-exports symbols** from other artifacts.

## Planning model

Before rendering, Dryv builds three indexes.

### 1. Artifact index

```text
artifact ID → output path
```

Example:

```text
User model → src/models/user.ts
Models barrel → src/models/index.ts
User service → src/services/user.service.ts
```

### 2. Symbol index

```text
symbol identity → defining artifact
```

Example:

```text
User → src/models/user.ts
UserService → src/services/user.service.ts
```

The symbol identity should be based on the IR item and declared template output, not only the text `User`.

### 3. Export index

```text
artifact → symbols it makes available
```

A normal file exports symbols it defines:

```text
user.ts exports User
```

A barrel exports symbols originating elsewhere:

```text
models/index.ts re-exports User
models/index.ts re-exports Order
```

Dryv retains both facts:

```text
User is defined by:
  src/models/user.ts

User is also available through:
  src/models/index.ts
```

## Import resolution

When a template requests `User`, Dryv resolves:

```text
requested semantic symbol
    ↓
defining artifact
    ↓
available export routes
    ├── direct file
    └── one or more barrels
```

The pack must explicitly determine which route is intended.

Possible decisions:

```text
Import directly from defining artifact
Import through a named barrel
Import through the nearest matching barrel
```

Dryv should not silently choose a barrel when several are available.

## Direct import

Consumer:

```text
src/services/user.service.ts
```

Provider:

```text
src/models/user.ts
```

Dryv calculates neutral path facts:

```text
consumer directory:
  src/services

source artifact:
  src/models/user.ts

relative segments:
  ..
  models
  user
```

The template renders them:

```jinja
{{ dependency.relative_segments | join_slash }}
```

Result:

```text
../models/user
```

Dryv does not write the import statement itself.

## Barrel import

Consumer:

```text
src/services/user.service.ts
```

Chosen barrel:

```text
src/models/index.ts
```

Dryv calculates relativity against the barrel, not the defining file:

```text
relative segments:
  ..
  models
```

The template may produce:

```text
../models
```

The trace still records:

```text
User
→ defined in user.ts
→ re-exported by models/index.ts
→ imported by user.service.ts through the barrel
```

## Efficient algorithm

Planning can run in near-linear time.

```text
1. Create all template invocations.
2. Calculate every artifact path.
3. Register symbols defined by each artifact.
4. Register barrel export relationships.
5. Build reverse index:
      symbol → available export artifacts
6. Resolve every import request through hash lookups.
7. Calculate relative path tokens.
8. Validate ambiguity, missing symbols, collisions, and cycles.
9. Render only after the graph is valid.
```

Approximate complexity:

```text
O(artifacts + symbols + exports + imports)
```

Dryv does not need to search every file for every import.

The important indexes are:

```text
symbol → defining artifact
symbol → barrel artifacts
artifact → exported symbols
template invocation → artifact
```

## Barrel cycles

Dryv should detect and reject unclear export cycles such as:

```text
models/index
→ exports domain/index

domain/index
→ exports models/index
```

Diagnostics should show the complete cycle before rendering.

## Information passed to templates

Each resolved import can expose:

```text
symbol name
symbol semantic identity
defining artifact
selected import artifact
whether imported directly or through a barrel
consumer artifact
relative path segments
source filename
source stem
source extension
```

The template remains responsible for:

* import syntax;
* path separators;
* extension removal;
* aliases;
* package imports;
* symbol aliases;
* combined imports.

## Important design rule

```text
Dryv resolves where a symbol is available.
The pack decides which export route to use.
The template decides how the import is written.
```

That gives efficient symbol resolution, correct relativity, barrel support, and complete traceability without requiring language adapters.

## Checklist update

**Artifact and symbol indexing** — `PROPOSED`
Use precomputed artifact, symbol, and export indexes.

**Barrel meaning** — `PROPOSED`
A barrel is a normal artifact that re-exports symbols from other artifacts.

**Import relativity** — `PROPOSED`
Calculate paths relative to the selected import artifact, which may be the defining file or a barrel.

**Barrel selection** — `UNREVIEWED`
We still need to decide whether packs must always name the barrel or may request a deterministic “nearest barrel” rule.
