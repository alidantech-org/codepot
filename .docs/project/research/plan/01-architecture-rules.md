# Architecture rules for implementing Codepot

## Rule 1 — one canonical semantic authority

The canonical Dryv Runtime IR is the only authority for portable software meaning.

Every semantic object, relation, facet, value, selector, and template-context property is owned and versioned by the runtime contract.

No authoring frontend, source adapter, pack, template, target adapter, plugin, CLI, or project configuration may create a competing semantic graph.

## Rule 2 — authoring compiles and stops

An authoring implementation may provide expressive language-native declarations, validation, references, and composition. Its output is:

```text
AuthoringResult
├── canonical contract or no contract
└── structured diagnostics
```

Authoring does not:

- select packs;
- select templates;
- choose output paths;
- render target syntax;
- write generated files;
- execute commands;
- own canonical JSON/YAML serialization;
- expose authoring builders to packs;
- preserve executable callbacks in IR.

## Rule 3 — canonical transport belongs to the runtime

JSON, YAML, binary, indexed, or other transport representations are encodings of the same canonical contract. The runtime owns:

- serialization;
- loading;
- canonical ordering;
- version markers;
- round-trip validation;
- digest calculation;
- migration and compatibility behavior.

Transport formats must not introduce new semantics.

## Rule 4 — the semantic kernel is closed and governable

Plugins and packs cannot add semantic kinds, relations, facets, selector grammar, expression roots, or context properties.

Unknown source metadata may be preserved as bounded immutable provenance, extensions, or raw values. Preservation does not grant meaning.

Kernel growth requires a formal versioned design change with validation, compatibility, selectors, contexts, fixtures, and migration rules.

## Rule 5 — schemas describe structure, not target syntax

A schema describes structural values such as primitives, literals, enums, objects, arrays, maps, tuples, unions, intersections, aliases, and unknown values.

Class, interface, record, struct, entity, DTO, request, response, table, model, component, and widget are not structural kinds. They may be generated vocabulary or controlled roles where explicitly approved.

Input/output direction belongs to schema use, not permanently to the schema.

## Rule 6 — behavior is explicit

Operations expose inputs, outputs, failures, effects, and approved facets. Workflows expose steps and transitions. Events, policies, storage mappings, and views are explicit relationships.

Convenience helpers may expand into these objects but may not create hidden behavior.

No endpoint, repository, storage mapping, form, event, or workflow is silently generated merely because a schema exists.

## Rule 7 — packs own emission, not meaning

A pack defines:

- which known semantic items it selects;
- why templates are selected;
- which immutable values templates receive;
- templates, partials, macros, and static files;
- generated destinations;
- symbols, imports, exports, and artifact dependencies;
- options and required project bindings;
- commands and approvals;
- compatibility requirements.

A pack does not redefine semantic objects or infer required meaning from undocumented conventions.

## Rule 8 — templates own every emitted character

Target-language syntax, imports, exports, annotations, framework calls, types, comments, validators, configuration, and documentation prose come from pack-owned templates or static files.

The runtime prepares facts and plans relationships. It does not secretly inject syntax.

## Rule 9 — target adapters provide facts, not renderers

A target adapter may:

- detect supported file kinds;
- validate identifiers and filenames;
- normalize target-aware paths;
- calculate module or import-specifier facts;
- expose bounded target capabilities.

It may not emit types, literals, imports, exports, annotations, validators, framework calls, or source text.

## Rule 10 — selectors are fixed, typed, and root-first

Packs use runtime-defined selectors with documented scope, ordering, singular context, and collection context.

Ordinary generation begins with outer ownership, such as groups and their contained schemas or operations. Packs do not receive an unrestricted graph query language.

New recurring selection needs are added through kernel/version governance, not ad hoc manifest expressions.

## Rule 11 — dependencies are declared before rendering

Generated consumers refer to selection keys and declared symbols. The planner resolves exact provider artifacts using semantic identity, scope, pack instance, symbol, and destination facts.

Missing, ambiguous, conflicting, and cyclic dependencies fail before rendering.

Templates receive immutable provider/module descriptors and author target syntax.

## Rule 12 — planning is complete before side effects

No renderer, writer, command runner, formatter, package manager, or external tool is called until the complete plan is valid.

The plan contains every:

- semantic invocation;
- artifact identity and destination;
- template/static origin;
- symbol and dependency;
- option and binding;
- command and approval;
- ownership action;
- compatibility result;
- collision and policy decision;
- explanation and impact edge.

## Rule 13 — full generation is the correctness reference

Implement deterministic full generation first. Incremental generation is an optimization that may be introduced only when impact can be proven conservatively.

When exact impact is uncertain, broaden regeneration. Never skip work based on an incomplete dependency model.

## Rule 14 — writes are managed and transactional

The writer distinguishes managed, unmanaged, modified, stale, and protected artifacts.

- unmanaged collisions fail by default;
- edited managed output is not overwritten silently;
- only unchanged stale managed output is removed automatically;
- staging precedes visible mutation;
- state commits after artifact commit;
- failure and cancellation restore the previous valid state;
- generation scopes are locked against unsafe concurrency.

## Rule 15 — configuration connects; it does not redefine

Project configuration owns input selection, pack instances, sources, outputs, options, bindings, overrides, and command policy.

Pack configuration owns generation behavior.

Neither file creates a new software model. Usage must remain the simplest tier.

## Rule 16 — sources and packs are reproducible

Local and Git sources resolve to explicit identities. Mutable Git refs are converted into immutable commits and content digests in a lock.

Credentials remain external and use normal Git mechanisms. They never appear in configuration, locks, state, diagnostics, or generated output.

## Rule 17 — commands are exact and controlled

Commands are explicit executable plus argument lists. The core does not invent package-manager syntax or transform dependency maps into commands.

Remote-pack commands require trust and approval according to host policy. Working directory, environment, timeout, cancellation, output capture, and allowed executables are controlled.

## Rule 18 — every frontend uses the same runtime operations

CLI, IDE, web, notebook, server, test harness, and AI/MCP integrations call one public runtime API.

No frontend receives hidden semantic or generation privileges. Human and machine presentations may differ, but behavior is shared.

## Rule 19 — diagnostics and explanations are contracts

Diagnostics have stable codes, severity, locations, semantic and pack identities, related facts, and remediation guidance.

Plans and trace reports explain selection, context, paths, dependencies, bindings, ownership, compatibility, and impact.

Logs are not a substitute for structured explanation artifacts.

## Rule 20 — stable identity is separate from naming and location

A semantic item’s identity does not automatically change when its display name, containing group, source file, or generated path changes.

Identity, naming projection, source provenance, and generated destination are separate facts. Renames and moves are explicit changes with compatibility consequences.

## Rule 21 — generated and handwritten ownership is explicit

Every artifact has a declared ownership strategy. Packs provide normal extension patterns through composition and neighboring handwritten modules.

Routine application logic should not require editing fully managed files. Generated regions are used only where their parsing and merge behavior can be proven safe.

## Rule 22 — determinism is observable

Every behavior-affecting input participates in plan and artifact digests:

- canonical contract and behavior version;
- packs and resolved sources;
- plugin identities and capabilities;
- templates, partials, static files;
- options, bindings, and overrides;
- target facts;
- relevant policy.

Environment-local facts that do not affect output remain outside canonical digests.

## Rule 23 — portability is tested, not assumed

Paths, casing, Unicode, line endings, executable permissions, symlinks, reserved names, and filesystem behavior are tested across supported platforms.

Canonical internal paths use one portable representation. Host conversion happens at controlled boundaries.

## Rule 24 — security uses least authority

Plugins, engines, pack providers, writers, caches, and command runners receive only the capabilities they need.

Remote content is untrusted until resolved, validated, locked, and approved. Template execution is sandboxed according to the engine’s risk model.

## Rule 25 — architecture tests protect boundaries

Automated tests enforce dependency direction and forbidden imports/behaviors, including:

- runtime independence from CLI and presentation libraries;
- authoring independence from generation and output;
- pack/template inability to mutate runtime semantics;
- domain layers independent from filesystem, Git, process, and terminal APIs;
- plugins using public contracts only;
- no process-global mutation during import.

## Rule 26 — active truth is explicit

Normative architecture documents are identified. Historical packages and archives are labeled. Verification status is dated and tied to a commit.

A contributor must be able to identify current product boundaries without reconstructing the rename history.

## Rule 27 — measure lifecycle value

Success is measured by change completion, consistency, compatibility defects caught, review effort, safe regeneration, migration cost, pack reuse, and user confidence.

Generated line count, number of supported languages, or marketplace size are not sufficient success metrics.

## Rule 28 — preserve an exit path

Projects can inspect and export canonical contracts, pin or own pack source, retain generated artifacts, stop generation deliberately, and migrate to another pack or handwritten implementation.

Portability includes the ability to leave.
