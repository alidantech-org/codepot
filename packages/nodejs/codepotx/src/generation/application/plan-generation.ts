import type {
  GenerationPlanRequest,
  GenerationPlanResult,
} from '@/contract/index';
import type { GenerationDependencies } from '../generation.types';
import { prepareGenerationPlan } from '../planning/prepare-generation-plan';
import { diagnostic, failure, success } from '../results';

export async function planGeneration(
  dependencies: GenerationDependencies,
  request: GenerationPlanRequest,
): Promise<GenerationPlanResult> {
  try {
    request.signal?.throwIfAborted();
    const prepared = await prepareGenerationPlan(dependencies, request);
    request.signal?.throwIfAborted();
    return prepared.success
      ? success(prepared.value.plan, prepared.diagnostics)
      : prepared;
  } catch (caught) {
    return failure([diagnostic('GENERATION_PLAN_CANCELLED', caught)]);
  }
}
