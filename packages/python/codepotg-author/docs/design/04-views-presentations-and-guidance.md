# Views, presentations, and guidance

## Views and parts

Views are group-owned neutral interaction units. A view can:

- reference schemas;
- contain nested parts;
- expose typed field/source uses;
- trigger operations;
- carry access facts, documentation, guidance, and tags.

A view is not inherently a page, screen, component, widget, command, or form. Packs choose emitted vocabulary.

## Presentations

A presentation is a proposed contract-level neutral application surface that composes views across groups.

Examples:

- organiser/admin application;
- customer application;
- driver mobile application;
- provider application;
- CLI application;
- desktop application;
- documentation portal;
- conversational surface.

A presentation may contain:

```text
identity
neutral channel
view placements
addresses (route, command, or other known address forms)
navigation connections
shell relationship
access
documentation/guidance/tags
```

A presentation does not contain framework names, widget trees, CSS, animations, state libraries, or target syntax.

## Ownership

```text
Group owns what a view means.
Presentation owns where that view participates in an application surface.
```

A presentation references views; it does not copy or inject them into groups. One view may be placed in several presentations. Distinct experiences may use distinct views while sharing schemas, operations, policies, and sources.

## Selection

If core approves presentations, it must publish fixed root-first selectors and bounded template contexts such as:

```text
presentations.each
presentations.entries.each
```

The author package cannot register those selectors itself.

## Guidance

Categorized information notes support explain, implement, warn, security, persistence, caching, testing, observability, UX, accessibility, and related documentation categories.

Guidance is descriptive. It never silently activates cache, access, storage, or rendering behavior. Typed semantics remain typed declarations.

Presentations and guidance are core evolution gates. They are never hidden author-only semantics when transported IR or templates need them.
