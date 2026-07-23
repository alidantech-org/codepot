import type {
  GenerationCommandRequest,
  GenerationCommandResult,
} from '@/contract/index';
import { executePlannedCommands } from '../command-execution';
import type { GenerationDependencies } from '../generation.types';
import { diagnostic, failure, success } from '../results';

export async function runGenerationCommands(
  dependencies: GenerationDependencies,
  request: GenerationCommandRequest,
): Promise<GenerationCommandResult> {
  try {
    const result = await executePlannedCommands({
      commands: request.plan.commands.filter(
        (command) => command.phase === request.phase,
      ),
      dryRun: request.dryRun ?? false,
      verbose: request.verbose ?? false,
      ...(request.signal ? { signal: request.signal } : {}),
    }, dependencies);
    return result.success
      ? success(result.outcomes, result.diagnostics)
      : failure(result.diagnostics);
  } catch (caught) {
    return failure([diagnostic('GENERATION_COMMAND_FAILED', caught)]);
  }
}
