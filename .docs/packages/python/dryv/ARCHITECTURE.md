# Dryv canonical runtime and server architecture

Status: approved architecture for the current refactor.

This document replaces the earlier AuthorSession/RenderSession-in-Runtime design. There is no compatibility requirement with that design.

## Governing three-tier model

```text
Authoring
    ↓
Canonical Dryv Runtime IR
    ↓
Templating
    ↓
Usage and generated output
```

Responsibilities are fixed:

- Authoring defines software meaning and produces Canonical Dryv Runtime IR.
- Canonical IR is the only semantic authority.
- Dryv Engine interprets usage configuration, Canonical IR and pack definitions and produces a deterministic `GenerationPlan`.
- Template packs define how Canonical IR becomes planned output.
- Render Clients understand template languages and turn `template + context` into generated artifact bytes.
- `dryv-api` coordinates builds, Render Clients, progress, streaming and optional bundle delivery.
- Project Clients collect local inputs, inspect diffs and are the only owners that mutate user filesystems.

## Canonical operational flow

```text
Any Authoring implementation
        ↓
Canonical Dryv IR
        │
Project Client
        ├── dryv.yaml
        ├── Canonical IR
        └── local pack bundles
                ↓
             dryv-api
                ↓ normalized Runtime input
           Dryv Runtime
                ↓
          GenerationPlan
                ↓
             dryv-api
                ├── renderer availability
                ├── template preflight
                ├── execution scheduling
                └── progress coordination
                ↓
          Render Clients
                ↓ generated artifacts
             dryv-api
                ├── artifact stream
                └── deterministic bundle
                ↓
          Project Client
                ↓ diff / approve / apply
          user filesystem
```

## Dryv Engine boundary

Dryv Engine consumes only normalized logical build inputs:

```text
RuntimeInput
├── usage configuration (`dryv.yaml`)
├── Canonical Dryv IR representation
└── pack inputs
    ├── pack manifest
    ├── logical template resource metadata
    ├── template content hashes
    └── other declared pack resources
```

Dryv Engine must never receive or own:

- HTTP requests or WebSocket objects;
- renderer URLs, connections, sessions or capacity;
- MCP requests;
- author source execution or Author Backends;
- Jinja, Handlebars or another template implementation;
- generated artifact byte streams;
- project-root paths or filesystem handles;
- local diff/apply state;
- shell or Git execution.

Any Canonical IR is accepted through the same Runtime path regardless of whether it came from Python, TypeScript, Rust, Codepot, another compiler, an AI tool, or a serialized hand-authored representation.

## Runtime work

The Runtime pipeline is:

```text
load usage configuration
    ↓
validate usage configuration
    ↓
load Canonical IR
    ↓
validate and index Canonical IR
    ↓
load and validate packs
    ↓
resolve pack options and relationships
    ↓
evaluate template selection
    ↓
build semantic and generation dependency graphs
    ↓
construct canonical template contexts
    ↓
resolve planned project-relative outputs
    ↓
hash relevant deterministic inputs
    ↓
produce GenerationPlan
```

Runtime stops at `GenerationPlan`. It does not render templates and does not create generated file bytes.

## GenerationPlan

`GenerationPlan` is the complete executable description of generation. `dryv-api` must be able to execute it without asking Runtime to reinterpret pack meaning.

A plan contains:

- build and input identities;
- required renderer capabilities;
- deterministic render jobs;
- semantic subjects and selection reasons;
- template logical resource IDs and hashes;
- canonical context values, context contracts and context hashes;
- planned artifact IDs and project-relative output paths;
- job/artifact dependencies and deterministic plan order;
- diagnostics;
- trace/provenance.

A render job conceptually contains:

```text
RenderJob
├── id
├── semantic subject
├── selection reason
├── renderer requirement
├── template reference + hash
├── canonical context + hash
├── context contract
├── planned outputs
└── dependencies
```

The Runtime owns why a template is selected, which values it receives and where its artifacts are planned. The Render Client owns every rendered byte.

## Runtime progress

Runtime may emit transport-neutral progress and diagnostic events through an observer/sink supplied by its caller.

Examples:

```text
runtime.started
config.loading
config.validated
ir.loading
ir.validated
pack.loading
pack.validated
graph.building
planning.started
planning.progress
context.created
plan.completed
diagnostic.warning
diagnostic.error
```

Runtime events contain data only. Runtime does not know whether they are displayed in a CLI, sent over WebSocket or translated into an agent tool update.

## Pack and template boundary

Dryv Runtime validates:

- `dryv.yaml` meaning;
- Canonical IR;
- `dryv.pack.yaml` meaning;
- pack selection and binding;
- context construction;
- planned output paths;
- semantic and artifact dependencies.

Template files are opaque resources to Runtime. Runtime knows their logical identity, hash, declared renderer requirement and the context contract supplied to them.

Render Clients validate:

- template-language syntax;
- renderer-specific helpers/features;
- compatibility with the supplied context contract;
- actual template execution.

A Render Client must not interpret Canonical IR, `dryv.yaml`, pack selection rules or project architecture.

## dryv-api boundary

`dryv-api` is execution and transport infrastructure around Dryv Runtime. It owns:

- HTTP build lifecycle;
- WebSocket build progress and renderer connections;
- build sessions and cancellation;
- uploaded logical resource normalization;
- renderer connection registry and capability inventory;
- template preflight coordination;
- renderer capacity and execution scheduling;
- bounded artifact streaming and backpressure;
- deterministic ZIP/bundle delivery;
- build status and transport diagnostics.

`dryv-api` does not reinterpret Canonical IR or pack semantics.

Renderer requirements are discovered from `GenerationPlan`, then matched to connected Render Clients. The API does not parse packs to derive renderer requirements independently.

## Render Client protocol

Every template implementation speaks one small renderer protocol:

```text
hello
validate
render
cancel
```

A Render Client receives only the material needed for rendering:

```text
template
+ context
+ planned output metadata
+ render options
```

It returns generated artifacts and renderer diagnostics.

The same protocol must support Jinja, Handlebars and future template engines without changing Dryv Runtime.

Template preflight should be reusable by the identity:

```text
templateHash
+ contextContractHash
+ rendererFingerprint
```

## Artifact delivery

Artifact execution and artifact delivery are separate concerns.

Supported API delivery modes are:

```text
stream
bundle
```

In stream mode, artifact metadata/content is forwarded through bounded streams.

In bundle mode, WebSocket still carries live progress and artifact metadata while the API creates a deterministic bundle for efficient HTTP download. A bundle contains a `.dryv/manifest.json` with artifact IDs, paths, hashes and provenance.

ZIP/bundle creation belongs to `dryv-api`, never to Dryv Runtime.

## Project Client boundary

Project Clients own:

- reading local `dryv.yaml` and Canonical IR files;
- resolving local pack paths into logical bundles;
- uploading required resources;
- observing WebSocket progress;
- receiving individual artifacts or downloading bundles;
- comparing generated output with local files;
- showing diffs and conflicts;
- safe extraction and path validation;
- filesystem mutation;
- shell/Git work when the client or agent supports it.

The Dryv server never requires the user's project root.

A simple Dryv CLI can therefore remain a thin Project Client. DevAuto can use the same server but add agent tooling, interactive diffs, approvals and terminal verification.

## Stateful server evolution

V1 may be stateless.

Later versions may remember authenticated accounts/projects and content-addressed resources. State is an optimization, never semantic authority.

Content identity is server-verified by cryptographic hash. A future server may reuse pack resources, templates, contexts, renders and bundles by hash and request only missing resources. Every build still identifies the exact configuration, IR, pack/template and renderer identities used.

## Non-negotiable boundaries

- Runtime IR is the only semantic authority.
- Runtime stops at `GenerationPlan`.
- No Author Backend execution exists inside Runtime.
- No Render Client connection/session exists inside Runtime.
- No template engine executes inside Runtime.
- No generated artifact bytes are owned by Runtime.
- No project filesystem mutation exists in `dryv` or `dryv-api`.
- No compatibility shims preserve the superseded execution architecture.
- `dryv-api` coordinates execution but does not redefine pack or IR meaning.
- Project Clients remain independently implementable, including TypeScript clients and AI-agent tooling.
