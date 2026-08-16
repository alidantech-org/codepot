# Task 02 — Render Client protocol and template preflight

Status: [ ]
Owner: `packages/python/dryv-api`
Depends on: Task 01

## Goal

Implement one renderer-neutral protocol for all template engines and perform early template/context compatibility checks before rendering begins.

## Protocol surface

`renderers/protocol.py` defines only the shared renderer protocol:

```text
hello
validate
render
cancel
```

Protocol data must support:

- renderer identity/version/fingerprint;
- declared capabilities;
- max concurrency;
- template logical resource identity/hash/content;
- canonical context values;
- context contract/version/hash;
- planned output metadata;
- render options;
- generated artifact metadata/chunks;
- renderer diagnostics and completion/failure.

Do not expose Canonical IR objects, `dryv.yaml` semantics or pack selectors to Render Clients.

## Connections and registry

`renderers/connection.py` owns one connected Render Client transport state.

`renderers/registry.py` owns the currently available renderer/capability inventory and connection lifecycle.

Runtime never sees these connection objects.

## Renderer requirement source

Renderer requirements come only from `GenerationPlan`.

The API must not parse pack definitions to rediscover renderer requirements.

If a required capability has no compatible Render Client, fail the build with an API-owned renderer-unavailable diagnostic before rendering.

## Template preflight

`renderers/preflight.py` asks the selected Render Client whether a template is syntactically valid and compatible with the context contract supplied by Runtime.

Preflight validates template-language concerns only.

Runtime remains the authority for context meaning and shape.

A reusable preflight identity is:

```text
templateHash
+ contextContractHash
+ rendererFingerprint
```

Identical preflight identities should not require repeated validation within the same build/session scope.

All required preflights must succeed before normal rendering begins unless a future explicitly approved execution mode changes this rule.

## Error ownership

Renderer/template diagnostics include concerns such as:

```text
TEMPLATE_SYNTAX_ERROR
UNKNOWN_CONTEXT_VARIABLE
MISSING_RENDERER_HELPER
UNSUPPORTED_RENDERER_FEATURE
```

Do not turn template-language failures into Runtime IR/pack errors.

## Code-size enforcement

Every production file must remain at or below 500 lines. Keep protocol, connection, registry and preflight responsibilities separate; do not merge them into a large generic renderer service.

## No-test gate

Do not create, modify or rewrite tests.

## Completion evidence

Inspect production code and confirm:

- one protocol can represent Jinja, Handlebars and future Render Clients;
- Render Clients receive only template/context/planned-output material;
- renderer requirements are read from `GenerationPlan`;
- preflight can report bad template variables before render execution;
- Runtime imports no renderer connection/session types;
- no production file exceeds 500 lines;
- no tests were changed.
