import type {
  Diagnostic,
  FileWriteOutcome,
  GenerationFileCounts,
  GenerationPlan,
  GenerationReport,
  RenderedGeneration,
} from '@/contract/index';

export function createGenerationReport(input: {
  readonly task: string;
  readonly status: GenerationReport['status'];
  readonly startedAt: number;
  readonly finishedAt: number;
  readonly plan: GenerationPlan;
  readonly rendered: RenderedGeneration;
  readonly files: readonly FileWriteOutcome[];
  readonly commandCount: number;
  readonly diagnostics: readonly Diagnostic[];
}): GenerationReport {
  return {
    task: input.task,
    status: input.status,
    durationMs: Math.max(0, input.finishedAt - input.startedAt),
    fileCounts: countGenerationFiles(input.plan, input.rendered, input.files),
    commandCount: input.commandCount,
    diagnostics: input.diagnostics,
  };
}

export function countGenerationFiles(
  plan: GenerationPlan,
  rendered: RenderedGeneration,
  files: readonly FileWriteOutcome[],
): GenerationFileCounts {
  const count = (status: FileWriteOutcome['status']): number => files.filter((file) => file.status === status).length;
  return {
    planned: plan.files.length,
    rendered: rendered.files.length,
    created: count('created'),
    updated: count('updated'),
    unchanged: count('unchanged'),
    skipped: count('skipped'),
    refused: count('refused') + plan.files.filter((file) => Boolean(file.refusalReason)).length,
    deleted: count('deleted'),
    rolledBack: count('rolledBack'),
  };
}
