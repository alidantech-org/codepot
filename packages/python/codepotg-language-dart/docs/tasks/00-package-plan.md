# Dart target adapter implementation plan

This package detects and validates Dart targets and calculates URI/path facts only. Flutter remains a template-pack concern. The adapter must not parse semantic sources, extend the kernel, render Dart syntax, select templates, plan destinations, write files, or execute commands.

## DART-001 — Package and plugin foundation

**Status:** planned

**Dependencies:** core plugin/target adapter ports and version primitives

- [ ] Add isolated package metadata, src layout, typing marker, README, and test configuration.
- [ ] Register `dart` in `codepotg.language_adapters`.
- [ ] Declare `.dart` target descriptor, behavior version, plugin/core/IR compatibility, and actual detection/validation/path capabilities.
- [ ] Implement immutable adapter factory/context.
- [ ] Add architecture tests proving no Flutter, source, engine, writer, CLI, filesystem, command, pack, private semantic-builder, or old-generator dependency.
- [ ] Add explicit tests prohibiting semantic/facet/selector registration and emitted source snippets.

## DART-002 — Typed target option schema

**Status:** planned

Define immutable options, patches only where permitted, descriptors, defaults, validation, restrictions, examples, and introspection for:

### Target files

- [ ] `.dart` suffix detection;
- [ ] Dart output filename/stem validation;
- [ ] path separator normalization;
- [ ] invalid/reserved filename diagnostics.

### Candidate identifiers

- [ ] Dart reserved words and contextual keywords;
- [ ] validation roles for types, enums, values, fields, parameters, libraries, prefixes, and file stems;
- [ ] Unicode/invalid-character/leading-digit/private-underscore validation facts;
- [ ] optional explicit escaping-validation facts without automatic semantic renaming.

### URI and module paths

- [ ] relative URI calculation;
- [ ] `package:` URI calculation from explicit package-name/project-path facts;
- [ ] explicit package/module URI validation;
- [ ] authored barrel/export provider destinations;
- [ ] containment and escaping diagnostics.

**Prohibited options:** generated naming transforms, type/null-safety mapping, literals, comments, import/export directives, prefixes/combinators, annotations, serialization, formatting, or Flutter policy.

**Acceptance:** introspection documents every allowed option and rejects every unknown or syntax-rendering path.

## DART-003 — Target resolver

- [ ] Implement deterministic `.dart` target detection.
- [ ] Preserve complete output filename after engine suffix removal.
- [ ] Produce stable target descriptor identity and diagnostics for unsupported/ambiguous suffixes.

## DART-004 — Filename and identifier validation

- [ ] Implement behavior-versioned reserved-word/contextual-keyword catalogs.
- [ ] Validate target filenames and declared candidate identifier roles.
- [ ] Preserve semantic-name and template/expression provenance in diagnostics.
- [ ] Return immutable facts rather than renamed strings or source snippets.
- [ ] Add property tests for deterministic valid/invalid boundaries.

## DART-005 — URI and project-path resolver

- [ ] Calculate relative URIs between already planned artifacts.
- [ ] Build `package:<name>/<path>` facts from explicit package-name and actual project-path bindings.
- [ ] Preserve and validate explicit package/URI strings.
- [ ] Resolve authored export/barrel provider destinations.
- [ ] Normalize separators and reject invalid/escaping paths.
- [ ] Never inspect template contents or choose output directories.

## DART-006 — Dependency module descriptors

- [ ] Consume immutable provider/consumer artifact and semantic dependency descriptors.
- [ ] Return URI, relative/package classification, provider destination, symbols, local dependency name, and diagnostics.
- [ ] Preserve semantic usage facts supplied by core.
- [ ] Do not deduplicate, prefix, defer, combine, order, quote, or render import/export directives.
- [ ] Do not return source-code snippets.

## DART-007 — Adapter facade

- [ ] Compose detection, validation, and URI/path services behind the public target adapter protocol.
- [ ] Accept immutable typed construction context/options.
- [ ] Expose target descriptors, capabilities, behavior identity, and diagnostics.
- [ ] Keep instances session-safe and free from global caches.
- [ ] Reject calls requesting type/literal/comment/import/export/annotation rendering.

## DART-008 — Conformance and negative boundaries

- [ ] Pass shared target-adapter conformance for declared capabilities.
- [ ] Add file/reserved-name/candidate-identifier validation cases.
- [ ] Add package URI, relative URI, project-path, export-provider, escaping, and deterministic path cases.
- [ ] Pass typed option, immutability, and session-isolation tests.
- [ ] Prove the package contains no TypeRenderer, LiteralRenderer, CommentRenderer, ImportPlanner/Renderer, ExportRenderer, annotation renderer, or formatter.
- [ ] Prove no Flutter widgets, state management, layout, pubspec ownership, or build-runner policy exists.
- [ ] Prove it cannot extend the semantic kernel, selector registry, expression roots, or render context.

## DART-009 — Integration with authored templates

- [ ] Provide planned dependency/URI facts to a fixture template.
- [ ] Have the template author Dart imports, exports, types, nullability, literals, comments, annotations, and client logic directly.
- [ ] Validate generated filenames/URIs without modifying rendered text.
- [ ] Assert exact output changes when templates change.
- [ ] Prove no adapter-generated line exists in output.

## DART-010 — Documentation and release

- [ ] Document all target options, descriptors, URI facts, and validation capabilities.
- [ ] Document relative versus `package:` path examples.
- [ ] Document strict template-owned syntax and unsupported services.
- [ ] Build wheel/sdist and validate compatibility.
- [ ] Publish independently from Dart and Flutter packs.

## Completion gate

- shared target-adapter conformance passes;
- every option/capability is typed, introspectable, and tested;
- relative/project/package URI facts resolve from actual planned paths;
- candidate validation never mutates semantic names;
- templates author every Dart character;
- no Flutter/framework/ecosystem/source/engine/writer/command/semantic-extension/syntax-rendering logic exists;
- behavior is deterministic and all inputs remain immutable.
