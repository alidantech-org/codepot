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
} from '../../operations/generation/index';

export interface GenerationPort {
  load(request: CodepotFileLoadRequest): Promise<CodepotFileLoadResult>;
  plan(request: GenerationPlanRequest): Promise<GenerationPlanResult>;
  render(request: GenerationRenderRequest): Promise<GenerationRenderResult>;
  write(request: GenerationWriteRequest): Promise<GenerationWriteResult>;
  clean(request: GenerationCleanRequest): Promise<GenerationCleanResult>;
  runCommands(request: GenerationCommandRequest): Promise<GenerationCommandResult>;
  execute(request: GenerationExecuteRequest): Promise<GenerationExecuteResult>;
}
