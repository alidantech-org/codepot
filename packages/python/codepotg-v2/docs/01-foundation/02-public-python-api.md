# Public Python API

## Primary product interface

The Python API is the primary CodepotG v2 interface. The CLI, MCP tools, HTTP services, playgrounds, notebooks, and IDE integrations call the same application services.

Generation logic must never depend on terminal arguments, `print`, `sys.exit`, or the process current directory.

## Supported facade

The high-level facade should support immutable construction:

```python
from codepotg import CodepotG

runtime = CodepotG.standard()
```

Hosts may provide explicit services and policies:

```python
runtime = CodepotG.create(
    plugin_registry=registry,
    pack_provider=provider,
    artifact_writer=writer,
    security_policy=policy,
    cache=cache,
)
```

## Core operations

The facade exposes synchronous and asynchronous variants of:

- configure a project or pack instance;
- validate project and pack configuration;
- inspect installed plugins and their rule schemas;
- inspect a pack contract;
- resolve Git/local packs and lock them;
- compile and inspect a complete generation plan;
- generate to memory, filesystem, or archive;
- inspect unresolved bindings and setup actions;
- approve or deny command capabilities;
- inspect cache and lock state.

The initial stable surface should prefer request objects:

```python
result = runtime.generate(
    GenerationRequest.from_project_file("codepotg.yaml")
)
```

Programmatic callers can construct typed requests without YAML:

```python
request = GenerationRequest(
    project=ProjectConfig(...),
    selected_packs=("server",),
    output_mode=OutputMode.MEMORY,
)
```

## Sessions

Each operation creates an isolated session containing:

- request identity;
- cancellation token;
- event sink;
- diagnostics;
- loaded source documents;
- normalized IR;
- resolved packs and plugins;
- effective rules;
- generation graph;
- staged artifacts;
- command approvals;
- cache scope.

A reusable runtime may serve concurrent requests, but session state must never leak between them.

## Results

Operations return structured result types instead of raising for expected validation failures.

Examples:

```text
ConfigureResult
ValidationResult
PlanResult
GenerationResult
PackResolutionResult
ApprovalResult
```

Every result contains:

- status;
- diagnostics;
- operation-specific data;
- events or event summary;
- readiness actions where applicable;
- stable serialization for MCP/HTTP boundaries.

Unexpected programming or infrastructure failures may raise typed exceptions at the API boundary after being converted into diagnostics where possible.

## Generation result status

Generation is not only success or failure. Supported readiness statuses are:

- `ready`;
- `generated_with_warnings`;
- `generated_with_actions`;
- `partially_generated`;
- `failed`;
- `cancelled`.

Fragment packs may generate useful output while reporting unresolved bindings, dependencies, or manual integration steps.

## In-memory operation

Playgrounds and servers must be able to avoid temporary output directories:

```python
result = runtime.generate(
    GenerationRequest(..., output_mode=OutputMode.MEMORY)
)

for artifact in result.artifacts:
    print(artifact.path, artifact.content)
```

Writers are ports, so the same plan can target:

- transactional filesystem output;
- memory;
- ZIP or tar archive;
- controlled object storage adapters.

## Events

The runtime emits structured events rather than terminal text:

```text
ConfigurationLoaded
PackResolved
PluginResolved
SourceLoaded
NormalizationStarted
NormalizationCompleted
PlanCompiled
ArtifactStarted
ArtifactCompleted
CommandApprovalRequired
TransactionCommitted
OperationFailed
```

CLI and server frontends format or stream these events independently.

## Async behavior

Async operations support:

- cancellation;
- deadlines supplied by the host;
- remote Git pack retrieval;
- event streaming;
- asynchronous artifact stores;
- approved subprocess execution.

The sync API may wrap the same application services, but it must not create nested event loops or hide cancellation.

## Server-safe defaults

`SecurityPolicy.server_safe()` should deny:

- project commands;
- pack commands;
- shell execution;
- network access except explicitly supplied pack/source providers;
- environment inheritance;
- filesystem access outside declared inputs and output staging.

A project or pack cannot weaken host policy.

## Public namespace policy

Supported extension imports should be exposed from stable modules such as:

```text
codepotg.api
codepotg.config
codepotg.ir
codepotg.generation
codepotg.plugins
codepotg.ports
codepotg.diagnostics
codepotg.testing
```

Internal modules are private and must not be used by adapters.
