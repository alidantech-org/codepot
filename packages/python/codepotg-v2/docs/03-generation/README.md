# 03 — Generation, planning, and output safety

## Processing pipeline

```text
load codepotg.yaml
→ decode and migrate typed ProjectConfig
→ resolve pack sources
→ load each CodepotgPack.yaml
→ discover and classify pack files
→ infer template engine and target syntax per file
→ resolve bindings, dependencies, rules, and setup requirements
→ evaluate selections and create TemplateInvocations
→ build template, artifact, import, and command graphs
→ validate all outputs, cycles, capabilities, and collisions
→ normalize source into neutral IR
→ render or copy into staging
→ compare exact content
→ commit the complete transaction
→ run permitted post-commit actions
```

There is no global language pipeline. The central unit is a `TemplateInvocation`: one template descriptor, one selected context or aggregate, one target syntax adapter, one template engine, effective typed rules, dependencies, bindings, and planned outputs.

## Selection and fan-out

Templates and static files may run once, once per record, once per group, or once over an aggregate. Folder patterns can apply shared selection and output defaults to every discovered file below a tokenized folder.

```yaml
filePatterns:
  "{module}/**":
    select:
      each: modules
      as: module
    output:
      root: src/modules/{module.directory}
```

A rendered template and an unchanged static README can therefore be emitted into every selected module. A single aggregate template may generate all models, operations, imports, and exports into one output file. Multiple named outputs are permitted only when all outputs are declared before rendering.

## Barrels and template composition

A barrel is a normal authored template with `role: barrel`. It receives typed planned export information, allowing comments, custom text, side-effect imports, framework conventions, and any target-language syntax. There is no system-owned root barrel key.

Template source inclusion, generated-code imports, and artifact dependencies are different contracts:

- includes compose template fragments through the pack template registry;
- semantic imports request symbols or bindings and are rendered by the target-language adapter;
- artifact requirements express planning dependencies without implying source inclusion or generated imports.

Composition must be visible during planning. Same-target fragments and neutral fragments are allowed by default; incompatible cross-language inclusion produces a diagnostic before rendering.

## Imports and bindings

Templates request logical symbols rather than calculating paths. The planner resolves providers and project bindings, then the language adapter applies relative, alias, package, namespace, barrel, extension, and conflict rules. Project-path bindings can become correct relative imports for every generated location; module and barrel bindings preserve the authored module specifier.

Raw imports remain an escape hatch but produce warnings because they cannot be relocated, deduplicated, or validated reliably.

## Static files

Every non-template pack file below the content root is copied by default unless ignored or explicitly classified as non-emitting documentation. Static means the content is unchanged; its output path may still be selected dynamically and repeated across modules or packages. Binary content must be supported without text decoding.

## Planning guarantees

Before rendering, CodepotG validates:

- every output stays within allowed roots;
- automatic discovery and explicit file configuration resolve to one descriptor;
- no two invocations silently produce the same path;
- every required capability has a provider or an allowed unresolved policy;
- provider, template, import, and command graphs are acyclic;
- target syntax and template engine adapters are installed and compatible;
- rule overrides are typed and permitted;
- command capabilities obey host, user, project, and pack security policies;
- owned, contributed, immutable, protected, and managed paths do not conflict.

Flexible mode can return `ready`, `generated_with_warnings`, `generated_with_actions`, or `partially_generated`. Strict mode rejects unresolved required bindings, dependencies, or manual actions.

## Transactional writes

All outputs are rendered or copied into staging. Exact content hashes determine changes; layout-insensitive comparison is forbidden. The writer validates ownership, unmanaged-file protection, clean scopes, symlinks, traversal, and collisions before committing. Failure before commit leaves the destination unchanged. A generation manifest records ownership and digests.

The cache is content-addressed and includes source digest, canonical IR version, plugin versions, pack commit and manifest digest, options, bindings, effective rules, template content, and output context. Cache hits must never bypass planning or safety validation.
