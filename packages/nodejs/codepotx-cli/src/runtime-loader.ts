import { createRequire } from 'node:module';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

import type { CodepotRuntimePort } from 'codepotx/contract';

interface RuntimeModule {
  createDefaultCodepotRuntime(options?: { readonly projectRoot?: string }): CodepotRuntimePort;
}

export async function loadProjectRuntime(projectRoot: string): Promise<CodepotRuntimePort> {
  const require = createRequire(resolve(projectRoot, 'package.json'));
  try {
    const localEntry = require.resolve('codepotx/runtime');
    const module = await import(pathToFileURL(localEntry).href) as RuntimeModule;
    return module.createDefaultCodepotRuntime({ projectRoot });
  } catch {
    const module = await import('codepotx/runtime') as RuntimeModule;
    return module.createDefaultCodepotRuntime({ projectRoot });
  }
}
