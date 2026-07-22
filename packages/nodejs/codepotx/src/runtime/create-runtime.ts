import type { CodepotRuntimePort } from '@/contract/index';

import { CodepotRuntime } from './runtime';
import type { RuntimeDependencies } from './runtime-dependencies.types';

export function createCodepotRuntime(dependencies: RuntimeDependencies): CodepotRuntimePort {
  return new CodepotRuntime(dependencies);
}
