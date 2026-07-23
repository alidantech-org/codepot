import { DefaultAuthoringCompiler, createAuthoringEngine } from '@/authoring/index';
import { createGenerationEngine } from '@/generation/index';
import { createDefaultPlatformServices } from '@/platform/index';
import { createTemplatingEngine } from '@/templating/index';
import { createCodepotRuntime } from '../create-runtime';
import type {
  DefaultCodepotRuntimeComposition,
  DefaultCodepotRuntimeOptions,
} from '../default-runtime.types';
import { DEFAULT_RUNTIME_FEATURES } from './default-features';

export function composeDefaultCodepotRuntime(
  options: DefaultCodepotRuntimeOptions = {},
): DefaultCodepotRuntimeComposition {
  const platform = options.platform ?? createDefaultPlatformServices(options);
  const compiler = new DefaultAuthoringCompiler({ hash: platform.hashes });
  const authoring = createAuthoringEngine({ ...platform, compiler });
  const templating = createTemplatingEngine(platform);
  const generation = createGenerationEngine({ ...platform, authoring, templating });
  const runtime = createCodepotRuntime({
    authoring,
    templating,
    generation,
    events: platform.events,
    clock: platform.clock,
    ids: platform.ids,
    features: DEFAULT_RUNTIME_FEATURES,
  });
  return { runtime, platform };
}

export function createDefaultCodepotRuntime(
  options: DefaultCodepotRuntimeOptions = {},
): DefaultCodepotRuntimeComposition['runtime'] {
  return composeDefaultCodepotRuntime(options).runtime;
}
