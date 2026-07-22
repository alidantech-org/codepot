import type {
  CodepotTaskConfig,
  CommandExecutionOutcome,
  Diagnostic,
  PlannedCommand,
} from '@/contract/index';

import type { GenerationDependencies } from './generation.types';
import { joinPath } from './planning';

const MAX_CAPTURED_OUTPUT = 1_000_000;

export interface ExecuteCommandsRequest {
  readonly commands: readonly PlannedCommand[];
  readonly dryRun: boolean;
  readonly verbose: boolean;
}

export interface ExecuteCommandsResult {
  readonly success: boolean;
  readonly outcomes: readonly CommandExecutionOutcome[];
  readonly diagnostics: readonly Diagnostic[];
}

export async function executePlannedCommands(
  request: ExecuteCommandsRequest,
  dependencies: Pick<GenerationDependencies, 'commands'>,
): Promise<ExecuteCommandsResult> {
  const outcomes: CommandExecutionOutcome[] = [];
  const diagnostics: Diagnostic[] = [];
  for (const command of request.commands) {
    const result = await dependencies.commands.run({
      command: command.command,
      cwd: command.cwd,
      environment: command.environment,
      optional: command.optional,
      dryRun: request.dryRun,
      verbose: request.verbose,
    });
    const outcome: CommandExecutionOutcome = {
      id: command.id,
      phase: command.phase,
      command: command.command,
      cwd: command.cwd,
      exitCode: result.exitCode,
      skipped: result.skipped,
      optional: command.optional,
      stdout: truncateOutput(result.stdout),
      stderr: truncateOutput(result.stderr),
    };
    outcomes.push(outcome);
    if (!result.skipped && result.exitCode !== 0) {
      diagnostics.push({
        code: command.optional ? 'GENERATION_OPTIONAL_COMMAND_FAILED' : 'GENERATION_COMMAND_FAILED',
        severity: command.optional ? 'warning' : 'error',
        layer: 'generation',
        message: `${command.optional ? 'Optional command' : 'Command'} failed with exit code ${result.exitCode}: ${command.command}`,
        details: {
          command: command.command,
          cwd: command.cwd,
          exitCode: result.exitCode,
          stderr: truncateOutput(result.stderr, 8_000),
        },
      });
      if (!command.optional) return { success: false, outcomes, diagnostics };
    }
  }
  return { success: true, outcomes, diagnostics };
}

/** Build commands before a GenerationPlan exists, preserving true before semantics. */
export function taskCommands(
  task: CodepotTaskConfig,
  projectRoot: string,
  phase: 'before' | 'after',
  ids: GenerationDependencies['ids'],
): readonly PlannedCommand[] {
  return task[phase].map((command) => ({
    id: ids.create('command'),
    phase,
    ...(command.name ? { name: command.name } : {}),
    command: command.run,
    cwd: joinPath(projectRoot, command.cwd ?? '.'),
    optional: command.optional ?? false,
    environment: { ...task.environment, ...(command.environment ?? {}) },
  }));
}

function truncateOutput(value: string, limit = MAX_CAPTURED_OUTPUT): string {
  if (value.length <= limit) return value;
  return `${value.slice(0, limit)}\n...[truncated ${value.length - limit} characters]`;
}
