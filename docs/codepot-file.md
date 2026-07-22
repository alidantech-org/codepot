---
title: CodepotFile.yml
description: Bind authored contracts and template packs to consumer-owned generation tasks.
order: 11
---

# `CodepotFile.yml`

```yaml
allow: true

defaults:
  output: ./generated
  transactional: true

sources:
  contracts:
    type: git
    repository: https://github.com/example/contracts.git
    ref: v1.2.0
    path: packages/contracts
    entry: codepotx.config.ts

  templates:
    type: package
    package: '@example/codepot-typescript'

 tasks:
  sdk:
    authoring: contracts
    templates: templates
    output: ./src/generated
    clean: [models, operations]
    variables:
      packageName: example-sdk
    before:
      - name: refresh contracts
        run: pnpm contracts:refresh
        optional: true
    after:
      - name: format output
        run: pnpm prettier --write src/generated
```

`allow: true` is required before task execution.

## Sources

Authoring and templates can come from local paths, packages, Git repositories, precompiled artifacts, or registered in-memory sources.

## Commands

Before commands run before source compilation. Required failures stop the task. Optional failures become warnings. Required after-command failures roll back a transactional task.

## Manifest

The default manifest is `.codepot/manifests/<task>.json`. Set `manifest` on a task to choose another project-relative path.
