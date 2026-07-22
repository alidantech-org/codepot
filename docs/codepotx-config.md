---
title: codepotx.config.ts
description: The modern authoring configuration contract.
order: 5
---

# `codepotx.config.ts`

```ts
import { defineCodepotConfig } from 'codepotx';
import { v1 } from './src/contracts/v1';

export default defineCodepotConfig({
  contracts: [v1],
  validation: {
    enabled: true,
    failOnWarnings: false,
  },
  diagnostics: {
    level: 'info',
  },
});
```

The file belongs to the authoring source. Template sources, output folders, cleanup, and project commands belong in `CodepotFile.yml`, not in authoring configuration.

The loader checks `codepotx.config.ts` first. A deprecated `package.config.ts` adapter may be used during migration, but new documentation and projects use only the canonical name.

Codepot loads reachable TypeScript imports with the consumer project's `tsconfig.json`, so aliases such as `@/*` remain owned by the consumer project.
