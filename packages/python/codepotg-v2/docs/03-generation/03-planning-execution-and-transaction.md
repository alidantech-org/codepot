# Planning, execution, and transactional output

## Complete plan before rendering

CodepotG compiles a complete immutable generation plan before any template renders or destination file changes.

The plan contains:

- resolved project and pack configuration;
- plugin and behavior versions;
- source digests and normalized IR identity;
- effective rules with provenance;
- file descriptors;
- template invocations;
- selected records and groups;
- resolved bindings;
- artifact providers and requirements;
- semantic imports and exports;
- output paths and lifecycle modes;
- dependency/manifest contributions;
- setup actions and commands;
- command capabilities and approval state;
- readiness and manual actions.

## Graphs

The planner builds explicit graphs for:

- template includes;
- artifact dependencies;
- provided and required capabilities;
- generated imports/exports;
- pack dependencies;
- command/action phase ordering;
- manifest contributions.

Cycles, missing providers, ambiguous providers, output collisions, incompatible targets, and forbidden capabilities are diagnosed before rendering.

## Template invocation

The central execution unit is `TemplateInvocation`, not a language-wide generation pipeline.

Each invocation contains:

- one file descriptor;
- one target adapter;
- one template engine;
- one selection instance or aggregate;
- effective rules;
- resolved bindings/imports;
- declared outputs;
- dependency order;
- immutable render context.

## Rendering

Rendering produces staged artifact content. Templates never receive destination filesystem handles.

Static and binary descriptors produce staged copy artifacts through the same plan and lifecycle validation.

## Writers

Artifact writers are ports:

- transactional filesystem writer;
- memory writer;
- archive writer;
- controlled external writers added later.

The filesystem writer stages the whole generation in a private area, validates it, then commits as one transaction as far as the platform safely permits.

## Path safety

Before staging:

- normalize separators;
- reject absolute paths unless an explicit writer contract owns them;
- reject traversal;
- enforce output roots;
- reject invalid/reserved segments;
- validate case-folded collisions where relevant;
- reject symlink escapes;
- validate managed/protected ownership.

## Exact comparison

Changed-content detection uses exact bytes or canonical line-ending policy declared by the writer. It must not ignore layout, comments, whitespace, or syntax-significant formatting.

## Ownership manifest

Committed output records:

- pack and instance identity;
- artifact ID;
- source file descriptor;
- content digest;
- lifecycle mode;
- generation session/lock identity;
- timestamp where needed outside deterministic content.

The manifest supports safe cleanup and unmanaged-file protection.

## Lifecycle

Supported intent includes:

- managed: CodepotG may replace or remove owned output;
- immutable: existing differing content is an error;
- protected: never overwrite without explicit project action;
- unmanaged: emit only when absent or according to explicit policy.

Project and host policies may tighten pack lifecycle requests.

## Rollback

Failures before commit leave destination state unchanged. Commit uses backup/replace operations and restores previous content on partial failure where supported.

The result must accurately report any platform limitation or incomplete rollback; it must not claim atomicity that did not occur.

## Dry run and inspect

Dry run compiles and, when requested, renders to memory without committing. It reports:

- files to create/change/delete/leave;
- manifest contributions;
- commands and approvals;
- unresolved bindings and manual actions;
- exact plugin, pack, and source versions.

## Cache

Content-addressed keys include all behavior-affecting inputs:

- source digest;
- IR version;
- source adapter version;
- target adapter behavior/rules version;
- template engine version/rules;
- pack commit and manifest/content digest;
- template/include digests;
- options/bindings/effective rules;
- selection identity;
- output-planning behavior version.

Cache collisions caused by omitted behavior inputs are correctness defects.

## Readiness

Flexible fragment generation can complete with explicit actions. Strict mode applies project/host readiness policy after planning and before commit.

Possible result states:

```text
ready
generated_with_warnings
generated_with_actions
partially_generated
failed
cancelled
```

## Tests

Required tests cover:

- all graph errors;
- deterministic plan ordering;
- no rendering before plan validity;
- static/template parity through planning;
- output collision and path safety;
- exact byte comparison;
- ownership and cleanup;
- transaction rollback;
- cancellation before commit;
- dry-run immutability;
- cache invalidation for every behavior input;
- honest readiness status.
