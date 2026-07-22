import { DefaultAuthoringCompiler, createAuthoringEngine } from '@/authoring/index';
import type { RuntimeFeature } from '@/contract/index';
import { createGenerationEngine } from '@/generation/index';
import { createDefaultPlatformServices } from '@/platform/index';
import { createTemplatingEngine } from '@/templating/index';

import { createCodepotRuntime } from './create-runtime';
import type {
  DefaultCodepotRuntimeComposition,
  DefaultCodepotRuntimeOptions,
} from './default-runtime.types';

const DEFAULT_FEATURES: readonly RuntimeFeature[] = [
  { id: 'authoring', version: '1', layer: 'authoring', capabilities: ['load', 'validate', 'compile', 'inspect', 'cache'] },
  { id: 'templating', version: '1', layer: 'templating', capabilities: ['load', 'validate', 'compile', 'context', 'render'] },
  { id: 'generation', version: '1', layer: 'generation', capabilities: ['load', 'plan', 'render', 'write', 'clean', 'commands', 'execute'] },
];

export function composeDefaultCodepotRuntime(
  options: DefaultCodepotRuntimeOptions = {},
): DefaultCodepotRuntimeComposition {
  const platform = options.platform ?? createDefaultPlatformServices(options);
  const compiler = new DefaultAuthoringCompiler({ hash: platform.hashes });
  const authoring = createAuthoringEngine({
    ...platform,
    compiler,
  });
  const templating = createTemplatingEngine(platform);
  const generation = createGenerationEngine({
    ...platform,
    authoring,
    templating,
  });
  const runtime = createCodepotRuntime({
    authoring,
    templating,
    generation,
    events: platform.events,
    clock: platform.clock,
    ids: platform.ids,
    features: DEFAULT_FEATURES,
  });
  return { runtime, platform };
}

export function createDefaultCodepotRuntime(
  options: DefaultCodepotRuntimeOptions = {},
): DefaultCodepotRuntimeComposition['runtime'] {
  return composeDefaultCodepotRuntime(options).runtime;
}
