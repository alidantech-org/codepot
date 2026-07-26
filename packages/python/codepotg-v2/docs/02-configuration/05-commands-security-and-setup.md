# Commands, security, and setup

## Purpose

Template packs may need to prepare, polish, or validate their output without forcing project users to understand internal templates. CodepotG therefore supports visible pack-owned actions and commands, project-owned commands, typed setup questions, and manual instructions.

Templates themselves cannot execute commands.

## Command ownership

### Project-global commands

Declared at `commands.before` and `commands.after` in `codepotg.yaml`. They run once around the selected pack sequence and are owned by the project.

### Project pack-instance commands

Declared at `packs.<instance>.commands`. They run around one configured pack instance and are project-owned.

### Pack-owned commands and actions

Declared in `CodepotgPack.yaml`. They are authored by the pack publisher and are governed by downloaded-pack trust policy.

The plan and approval UI must always show the command owner.

## Structured command model

Raw commands use structured fields:

```yaml
- id: format-generated
  executable: pnpm
  arguments: [prettier, --write, "{output.root}"]
  cwd: "{project.root}"
  timeoutSeconds: 120
  optional: true
  permissions:
    filesystem:
      read: ["{output.root}"]
      write: ["{output.root}"]
    network: false
    environment:
      inherit: [PATH]
```

A shell string is not the default representation. Shell mode is a separate high-risk capability.

## Typed actions

Common operations should be ecosystem actions rather than hardcoded commands:

```text
node.project.detect
node.packageManager.resolve
node.dependencies.ensure
node.script.run
node.eslint.fix
node.format
node.typecheck
dart.dependencies.get
dart.buildRunner.run
dart.format
codepotg.generate
```

The ecosystem adapter resolves the actual executable and arguments using project toolchain configuration.

Typed actions remain security-sensitive because package installation can execute lifecycle scripts.

## Desired state versus action

A pack declares desired manifest contributions separately:

```yaml
dependencies:
  node:
    runtime:
      typeorm: "^0.3.0"
```

Then it may recommend an action:

```yaml
setup:
  actions:
    after:
      - action: node.dependencies.ensure
```

This allows users and servers to accept manifest changes but deny process execution.

## Security hierarchy

Final permission is the strictest result of:

1. host policy;
2. user policy;
3. project policy;
4. pack declaration;
5. exact approval record.

A project or pack cannot weaken host policy.

## Recommended modes

### Local trusted project

- project commands: allow;
- pack commands: require approval;
- shell: require explicit approval;
- network: require explicit capability;
- environment inheritance: allowlist only.

### Newly cloned or untrusted project

- project commands: require approval;
- pack commands: require approval;
- secrets: deny;
- shell: deny unless explicitly approved.

### Server, playground, or MCP host

- all commands: deny by default;
- filesystem limited to controlled inputs and staging;
- no environment inheritance;
- no secrets;
- network only through supplied providers.

## Capabilities

Commands and actions request explicit capabilities:

```text
executeProcess
useShell
readProject
writeProject
readOutput
writeOutput
network
inheritEnvironment
accessSecrets
writeOutsideOutput
```

High-risk capabilities require stronger approval and may be forbidden by host policy.

## Approval identity

An approval is tied to:

- project identity;
- pack repository or local identity;
- resolved Git commit;
- pack subdirectory;
- pack manifest digest;
- command or action ID;
- exact executable and arguments or typed action payload;
- working directory;
- capability set;
- environment allowlist;
- approval scope: once or exact digest.

A changed command, pack commit, manifest, or capability request invalidates the approval.

## Environment

Commands do not inherit the complete process environment.

Default visible values are limited to controlled platform values such as `PATH` and CodepotG-defined paths. Secrets require an explicit host-provided secret reference and must never be serialized to project files, lock files, diagnostics, or generated setup reports.

## Transaction phases

Every action declares where it runs:

- before source preparation;
- before planning;
- before rendering;
- on staged output before commit;
- after commit;
- on failure.

Only staged-output actions can participate in the file transaction. A post-commit type check cannot be rolled back as though it were atomic with generation.

## Setup contract

A pack setup contract contains:

- summary;
- documentation;
- typed questions tied to options or bindings;
- project detection hints;
- dependency recommendations;
- before/after actions;
- manual steps;
- readiness explanations.

`codepotg configure` executes the setup conversation through typed application operations. CLI, MCP, and web frontends can render the same questions.

## Manual steps

Manual integration is first-class, not treated as generator failure.

Examples:

- configure TypeORM connection;
- register generated repositories;
- add a generated Dart package to a workspace;
- import a generated module from the host application.

Generation results include unresolved manual steps and may optionally emit an authored setup report when the pack declares one.

## Tests

Required tests cover:

- ownership and trust classification;
- strict policy precedence;
- command digest stability;
- approval invalidation;
- environment filtering;
- timeout and process cleanup;
- staged versus post-commit phases;
- optional versus required command failure;
- typed action resolution for npm, pnpm, Yarn, and Dart;
- server-safe denial behavior.
