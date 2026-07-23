import type {
  CodepotFileLoadRequest,
  CodepotFileLoadResult,
  GenerationCleanRequest,
  GenerationCleanResult,
  GenerationCommandRequest,
  GenerationCommandResult,
  GenerationExecuteRequest,
  GenerationExecuteResult,
  GenerationPlanRequest,
  GenerationPlanResult,
  GenerationRenderRequest,
  GenerationRenderResult,
  GenerationWriteRequest,
  GenerationWriteResult,
} from '@/contract/index';
import { cleanGeneration } from './application/clean-generation';
import { executeGeneration } from './application/execute-generation';
import { loadCodepotFile } from './application/load-codepot-file';
import { planGeneration } from './application/plan-generation';
import { renderGeneration } from './application/render-generation';
import { runGenerationCommands } from './application/run-generation-commands';
import { writeGeneration } from './application/write-generation';
import type {
  GenerationDependencies,
  GenerationEngine,
} from './generation.types';

/** Public generation facade over focused application use cases. */
export class DefaultGenerationEngine implements GenerationEngine {
  readonly #dependencies: GenerationDependencies;

  constructor(dependencies: GenerationDependencies) {
    this.#dependencies = dependencies;
  }

  load(request: CodepotFileLoadRequest): Promise<CodepotFileLoadResult> {
    return loadCodepotFile(this.#dependencies, request);
  }

  plan(request: GenerationPlanRequest): Promise<GenerationPlanResult> {
    return planGeneration(this.#dependencies, request);
  }

  render(request: GenerationRenderRequest): Promise<GenerationRenderResult> {
    return renderGeneration(this.#dependencies, request);
  }

  write(request: GenerationWriteRequest): Promise<GenerationWriteResult> {
    return writeGeneration(this.#dependencies, request);
  }

  clean(request: GenerationCleanRequest): Promise<GenerationCleanResult> {
    return cleanGeneration(this.#dependencies, request);
  }

  runCommands(
    request: GenerationCommandRequest,
  ): Promise<GenerationCommandResult> {
    return runGenerationCommands(this.#dependencies, request);
  }

  execute(request: GenerationExecuteRequest): Promise<GenerationExecuteResult> {
    return executeGeneration(this.#dependencies, request);
  }
}

export function createGenerationEngine(
  dependencies: GenerationDependencies,
): GenerationEngine {
  return new DefaultGenerationEngine(dependencies);
}
