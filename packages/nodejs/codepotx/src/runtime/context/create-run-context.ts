import type { RunContext } from '@/contract/index';
import type { RuntimeDependencies } from '../runtime-dependencies.types';

export function createRunContext(
  dependencies: Pick<RuntimeDependencies, 'ids'>,
  input: Partial<RunContext> | undefined,
): RunContext {
  return {
    runId: input?.runId ?? dependencies.ids.create('run'),
    requestId: input?.requestId ?? dependencies.ids.create('request'),
    ...(input?.projectRoot ? { projectRoot: input.projectRoot } : {}),
    ...(input?.task ? { task: input.task } : {}),
    ...(input?.signal ? { signal: input.signal } : {}),
    ...(input?.metadata ? { metadata: input.metadata } : {}),
  };
}
