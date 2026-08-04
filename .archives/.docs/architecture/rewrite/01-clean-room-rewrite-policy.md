# Clean-room Dryv policy

## Purpose

Dryv is a new runtime architecture in the Codepot ecosystem. It does not rename, import, or wrap the archived generator implementation.

The archived package retains its original name, history, behavior, and release line. Dryv uses distinct distributions and namespaces.

## Allowed historical reference

Developers may inspect archived projects to identify:

- real semantic needs and reusable intent;
- representative outputs;
- template capabilities users rely on;
- performance and scale requirements;
- useful diagnostics;
- safety failures to avoid;
- realistic acceptance fixtures.

Historical observation does not authorize importing or copying old runtime architecture.

## Prohibited reuse

Dryv must not copy or restore:

- import-time rewriting or monkey patching;
- same-name module/package collisions;
- CLI manipulation of `sys.path` or `sys.modules`;
- global decorator plugin registries;
- internal directory plugin scanning;
- provider-specific data in target plugins or template contexts;
- duplicate semantic or generation representations;
- template-source scanning as hidden dependency planning;
- unsandboxed template contexts;
- shell-string command execution defaults;
- per-file transactions presented as whole-generation safety;
- overwritten duplicate output maps;
- mutable internals hidden in frozen containers.

## No compatibility runtime

Dryv does not implement:

- archived task/configuration decoders;
- project-level target-language switching;
- `templateDir` or `paths.yaml` fallbacks;
- old generator execution paths;
- wrappers around archived language implementations;
- import aliases pointing to archived modules.

This prevents old separation-of-concern failures from becoming permanent Dryv dependencies.

## Re-authoring approach

Migration is explicit re-authoring:

- semantic meaning becomes a public Dryv contract;
- orchestration becomes `dryv.yaml`;
- reusable generation behavior becomes `DryvPack.yaml` plus pack files;
- each pack owns templates, partials, static files, selectors, options, bindings, and declared commands;
- targets are inferred per planned artifact;
- command execution remains explicit and separately trusted.

Dryv may provide documentation and analysis tools that help users understand archived files, but the runtime dependency graph stays clean.

## Output comparison

Behavioral comparison does not require architectural compatibility.

For each re-authored pack:

1. create a small inspectable Dryv fixture;
2. create a realistic fixture;
3. compare intended behavior and outputs;
4. classify differences as intentional improvements or defects;
5. repair accidental differences in the new implementation;
6. never add an archived execution path solely to preserve an implementation quirk.

## Release gate

Dryv releases only after:

- architecture and security tests pass;
- authoring and plugin packages pass public contracts;
- realistic packs generate valid projects;
- runtime and standalone CLI workflows pass;
- direct IR and in-memory Python authoring are verified;
- Git/lock and command trust lanes are safe when enabled;
- cookbook and migration guidance are current;
- isolated package installation proves no namespace collision with the archived line.
