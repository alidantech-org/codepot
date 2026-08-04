# `paths.yaml` and `paths.yml` Graph Guide

CodepotG accepts either `paths.yaml` or `paths.yml` in one template pack. A pack must not contain both names.

The graph contract separates three concerns:

```text
selection  -> chooses source data
emission   -> renders one template from a selection
tbarrel    -> aggregates outputs from emissions or other barrels
```

`folders` remains supported as the legacy compatibility format. New packs should use named selections and emissions.

## Complete example

```yaml
imports:
  strategy: relative

write_policy:
  default_mode: managed
  managed_roots: [generated]
  immutable_roots: [generated/bootstrap]
  protected_roots: [src/manual]
  clean_roots: [generated]

selections:
  dtos:
    select: schemas.emit_dtos
    as: dto
    scope: each

  enums:
    select: schemas.emit_enums
    as: enum
    scope: each

  resource_operations:
    select: operations
    as: operations
    scope: resource

emissions:
  dto-types:
    selection: dtos
    template: templates/dto.type.ts.j2
    output: [generated, models, "[dto.name.path.o].ts"]
    provides: [dtos]

  dto-zod:
    selection: dtos
    template: templates/dto.zod.ts.j2
    output: [generated, schemas, "[dto.name.path.o].schema.ts"]
    provides: [dtos, validation]
    imports:
      enums: enum-types

  enum-types:
    selection: enums
    template: templates/enum.ts.j2
    output: [generated, models, "[enum.name.path.o].ts"]
    provides: [enums]

  operations:
    selection: resource_operations
    template: templates/resource.operations.ts.j2
    output: [generated, resources, "[selection.resource]", operations.ts]
    imports:
      dtos: dto-types
      enums: enum-types

barrels:
  models:
    template: templates/models.index.ts.j2
    output: [generated, models, index.ts]
    exports: [dto-types, enum-types]
    scope: all

  resource_models:
    template: templates/resource.index.ts.j2
    output: [generated, resources, "[barrel.resource]", index.ts]
    exports: [dto-types, enum-types]
    scope: resource
```

## Selections

A selection has a stable name independent of any template:

```yaml
selections:
  dtos:
    select: schemas.emit_dtos
    as: dto
    scope: each
```

Fields:

| Field | Required | Meaning |
|---|---:|---|
| `select` | yes | Documented source collection or canonical selection expression. |
| `as` / `alias` | no | Context variable used by templates and output expressions. Defaults to the selection name. |
| `scope` | no | `each`, `all`, or `resource`. Defaults to `each`. |
| `description` | no | Author-facing explanation displayed by `codepotg paths`. |

Selection aliases must be unique. `as` and `alias` are compatibility names for the same field and may not conflict.

### Selection scopes

`each`
: One output context per selected item. The alias is the selected item.

`all`
: One output context containing every selected item. The alias is an ordered tuple. `selection.count` reports its size.

`resource`
: One output context per resource. The alias is the ordered tuple belonging to that resource. `selection.resource` contains the resource identity.

The same selection can feed several emissions. CodepotG resolves the selection once, then each emission gets its own template, output path, providers, lifecycle, and result.

## Emissions

An emission is one named output producer:

```yaml
emissions:
  dto-types:
    selection: dtos
    template: templates/dto.type.ts.j2
    output: [generated, models, "[dto.name.path.o].ts"]
    provides: [dtos]
    imports:
      enums: enum-types
```

Fields:

| Field | Required | Meaning |
|---|---:|---|
| `selection` | yes | Name from `selections`. |
| `template` | yes | Safe relative template path. `..` and absolute paths are refused. |
| `output` | yes | Non-empty list of static and dynamic path parts. |
| `provides` | no | Semantic capabilities supplied by the output, such as `dtos`, `enums`, or `entities`. Defaults to the selection name. |
| `imports` | no | Mapping of dependency purpose to an explicit emission or barrel provider. |
| `lifecycle` | no | `managed` or `immutable`. Defaults to the write-policy mode. |
| `description` | no | Author-facing explanation. |

Output paths are normalized to relative POSIX paths before files exist. Collisions are rejected during planning.

## Explicit dependency providers

A dependent emission must identify its providers:

```yaml
emissions:
  operations:
    selection: operations
    template: operation.ts.j2
    output: [generated, operations, "[operation.name.path.o].ts"]
    imports:
      dtos: dto-types
      enums: enum-types
```

CodepotG resolves each required source ref against only these configured providers. Generation fails when:

- no configured provider emits the required ref;
- more than one configured provider emits the same required ref;
- the provider name does not exist;
- a provider output is ambiguous for the required resource scope.

Conflict validation uses actual effective refs, not only broad categories. A barrel containing enums and a direct DTO provider are valid together. A barrel and a direct provider that both contain the same required DTO are rejected.

## Barrels

A barrel is a first-class output node:

```yaml
barrels:
  models:
    template: models.index.ts.j2
    output: [generated, models, index.ts]
    exports: [dto-types, enum-types]
    scope: all
```

Fields:

| Field | Required | Meaning |
|---|---:|---|
| `template` | yes | Barrel template. |
| `output` | yes | Barrel output path. |
| `exports` | yes | One or more emission or barrel node names. |
| `scope` | no | `all` or `resource`. `each` is invalid for barrels. |
| `as` / `alias` | no | Barrel context variable. Defaults to `barrel`. |
| `lifecycle` | no | `managed` or `immutable`. |

A barrel template receives:

```text
barrel.name
barrel.scope
barrel.resource
barrel.members
barrel.symbols
barrel.provides
barrel.count
```

Each member is a virtual output with its source ref, output path, symbols, capabilities, resource, and status.

Barrels are not handled by a fixed “all barrels last” pass. The scheduler writes a barrel only after every member in its declared scope has been physically written or accepted as an existing immutable output. Nested barrels are scheduled through the same dependency graph.

## Bounded graph template context

Graph templates receive bounded globals:

```text
project
lang
emit
meta
selected_frontend
selected_frontends
frontend_count
file
output
providers
provider_outputs
selection
source
sources
resolve
resolver_stats
```

They also receive their declared selection alias, such as `dto`, `enum`, `operation`, or `resource`.

The complete `api`, `schemas`, `operations`, `resources`, `entities`, and `frontends` roots remain internal selection sources and are not copied into graph render contexts.

### `selection`

```text
selection.name
selection.select
selection.alias
selection.scope
selection.key
selection.item
selection.items
selection.resource
selection.count
```

### `source` and `sources`

`source` is a lazy indexed JSONL proxy when the output represents one source ref. `sources` is the ordered tuple for aggregate output.

Metadata such as `source.key`, `source.ref`, `source.kind`, and `source.resources` does not load the raw record. Mapping access triggers one indexed byte lookup:

```jinja
{{ source.kind }}
{{ source.get("description", "-") }}
{% for value in source.get("enum", ()) %}
  {{ value }}
{% endfor %}
```

### `resolve`

The bounded resolver supports:

```jinja
{% set user = resolve.ref("#/components/schemas/User") %}
{% set operation = resolve.operation("listUsers") %}
{% set resource_items = resolve.resource("users") %}
{% set users = resolve.mentions("tag", "users") %}
{% set dependants = resolve.dependants("#/components/schemas/User") %}
```

Returned objects remain lazy. Resolver caches enforce record-count, byte, related-item, and depth limits.

## Dynamic output parts

An output part may be static or dynamic:

```yaml
output:
  - generated
  - resources
  - "[selection.resource]"
  - "[operation.name.path.o].ts"
```

The existing path token rules remain available:

```text
[expression]   dynamic value
[[value]]      literal bracketed value
{{value}}      literal braced value
```

## Write lifecycle and safety

`managed`
: CodepotG creates and updates changed content.

`immutable`
: CodepotG creates the file once. Existing files are accepted as written dependencies without being modified.

All generated writes are atomic. A temporary sibling file is flushed and then replaced into place. Protected roots, out-of-root writes, invalid lifecycle roots, and output collisions are refused before rendering.

## Incremental scheduling

The graph runtime operates as:

```text
ready selection outputs
  -> bounded render workers
  -> byte-bounded file queue
  -> one atomic file writer
  -> written registry update
  -> release dependants
```

Progress states include selection resolution, planned, rendering, rendered, queued, written, unchanged, immutable skipped, failed, and completed.

## Legacy `folders` migration

Legacy packs continue to work:

```yaml
folders:
  dto:
    select: schemas.emit_dtos
    as: dto
    mode: each
    parts: [generated, models]
```

Migration steps:

1. Create a named selection from each distinct legacy `select` expression.
2. Create one named emission for each template/output behavior.
3. Move the template path and complete output path into the emission.
4. Add `provides` to provider outputs.
5. Add explicit `imports` to dependent emissions.
6. Replace aggregate index templates with barrels.
7. Run `codepotg paths <template-directory>` before generation.
8. Keep the legacy folder block temporarily when comparing output, then remove it after compatibility tests pass.

A pack may contain both legacy folders and the new graph while migrating. Explicit graph templates are planned only from graph declarations; legacy template scanning remains isolated to folder-only packs.

## Validation command

```bash
codepotg paths path/to/template-pack
```

The command reports:

- legacy folder recipes;
- named selections and scopes;
- emissions, output paths, capabilities, and provider edges;
- barrels, scopes, and export membership;
- unknown keys and invalid references;
- dependency cycles and unsafe template paths.


---------------------------- info about improvemenet ----------------------------------------------
Good problem to dig into — this spec already has solid bones (explicit providers, atomic writes, typed scopes), so the improvements here are mostly about reducing ambiguity and boilerplate rather than redesigning anything. In priority order:

**1. Fix the actual bug first**
The concerns list says: `selection -> chooses source data; emission -> renders one template; tbarrel -> aggregates outputs`. Everywhere else in the doc it's `barrel`, not `tbarrel`. This is a small thing, but it's a perfect illustration of the AI-friendliness problem: if a doc has an inconsistent term, an LLM ingesting this spec to generate a `paths.yaml` may pattern-match on either name and produce invalid config with total confidence. Fix typos like this aggressively — they cost humans a raised eyebrow and cost AI tooling a silent failure.

**2. Ship a JSON Schema for `paths.yaml`**
This is the single highest-leverage change for both audiences. With a real schema (yaml-language-server compatible):
- Humans get autocomplete + inline validation in their editor instead of discovering typos via `codepotg paths` or a failed generation.
- An AI agent editing the file can validate its own output *before* running generation, instead of guessing at valid keys/enums from prose docs and hoping.
- You can enforce context-specific enums properly — e.g. right now barrels silently reject `scope: each` as a runtime error ("`each` is invalid for barrels"). If `SelectionScope` and `BarrelScope` are two distinct schema types instead of one shared `each|all|resource` enum, that becomes a compile-time/schema-time impossibility instead of a generation-time failure. Fewer states you can even represent = less for anyone (human or model) to get wrong.

**3. Collapse the bracket dialects in output paths**
Right now one field can contain three different token syntaxes: `[expression]` (dynamic), `[[value]]` (literal bracket), `{{value}}` (literal brace). That's three conventions to memorize for two concepts (dynamic vs. literal), inside a system that *already* uses Jinja everywhere else. Every extra syntax is a place an LLM will regress to whichever templating style it's seen more of in training (almost certainly `{{ }}` for *everything*, including where you meant literal). I'd either:
- reuse actual Jinja delimiters for dynamic parts (`{{ dto.name.path.o }}.ts`) since templates already speak Jinja, and treat anything without delimiters as literal — no escaping mini-language needed, or
- if you need to keep a distinct DSL for other reasons, document it as a tiny formal grammar (3 rules) right next to every example, not just in one "Dynamic output parts" section readers may skip.

**4. Kill the `as` / `alias` duplication**
Selections and barrels both accept `as` or `alias` for the same field, with a rule that they "must not conflict." Two spellings of one concept doubles the surface an AI has to consider (which one is canonical? do I need both?) for zero added expressiveness. Pick `as`, keep `alias` as a silently-normalized deprecated input if you need back-compat, but don't document them as two equally valid choices.

**5. Reduce boilerplate for the 80% case**
Every emission needs a separately-declared `selections:` entry, even when nothing else reuses that selection. For the common case — one selection feeding exactly one emission — that's two objects to write and mentally link via a name, every time. Consider letting an emission declare `select:` inline directly:

```yaml
emissions:
  dto-types:
    select: schemas.emit_dtos      # implicit private selection
    as: dto
    template: templates/dto.type.ts.j2
    output: [generated, models, "{{ dto.name.path.o }}.ts"]
```

...and only require the explicit `selections:` block once a selection is actually shared by more than one emission. This is standard progressive disclosure: simple things should look simple, and an AI generating a one-off pack shouldn't have to reason about sharing semantics it doesn't need yet.

**6. Document the `.pascal.o` / `.path.o` convention explicitly, once, in one place**
It shows up in every template you've shared (`.pascal.o`, `.camel.o`, `.path.o`) but I never saw its shape defined anywhere in these docs. Unexplained terse suffixes like `.o` are exactly what causes an LLM to guess plausible-but-wrong usage on an edge case (what happens for a name with no valid identifier form? what does `.o` even stand for?). A single "Name object reference" table — every accessor, what it returns, one example each — pays for itself every time someone (human or AI) writes a new template.

**7. Make `codepotg paths` machine-readable**
It already reports selections, emissions, barrels, cycles, and unsafe paths — genuinely good. Add a `--json` flag so an agent can consume that dependency graph programmatically (to auto-fix a missing `imports:` entry, for instance) instead of scraping CLI text. Same idea for generation failures: "more than one configured provider emits the same required ref" should come back as structured data (`{ref, providers: [...], emission}`), not just prose — that's the difference between an AI agent that can propose a fix and one that can only tell you it broke.

The common thread: almost everything above is about **collapsing ambiguity into schema** wherever possible, so both a human's editor and an AI's validation pass catch mistakes before generation runs, rather than during it.