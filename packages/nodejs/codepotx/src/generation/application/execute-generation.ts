import type {
  CodepotTaskConfig,
  CommandExecutionOutcome,
  Diagnostic,
  GenerationExecuteRequest,
  GenerationExecuteResult,
  GenerationResult,
} from '@/contract/index';
import { findTask } from '../codepot-file';
import {
  executePlannedCommands,
  taskCommands,
} from '../command-execution';
import { GenerationEventPublisher } from '../generation-events';
import type { GenerationDependencies } from '../generation.types';
import { applyManagedWrite, ManagedWriteError } from '../managed-write';
import { prepareGenerationPlan } from '../planning/prepare-generation-plan';
import { createGenerationReport } from '../report';
import { diagnostic, failure, success } from '../results';
import { loadCodepotFile } from './load-codepot-file';
import { renderGeneration } from './render-generation';

export async function executeGeneration(
  dependencies: GenerationDependencies,
  request: GenerationExecuteRequest,
): Promise<GenerationExecuteResult> {
  try {
    request.signal?.throwIfAborted();
    const loaded = await loadCodepotFile(dependencies, request.codepotFile ?? {});
    if (!loaded.success) return loaded;
    let tasks: readonly CodepotTaskConfig[];
    try {
      tasks = request.allTasks
        ? loaded.value.tasks
        : [findTask(loaded.value, request.task)];
    } catch (caught) {
      return failure([
        diagnostic('GENERATION_TASK_SELECTION_FAILED', caught),
      ]);
    }

    const results: GenerationResult[] = [];
    for (const task of tasks) {
      request.signal?.throwIfAborted();
      const events = new GenerationEventPublisher(dependencies);
      const startedAt = dependencies.clock.monotonicMilliseconds();
      const dryRun = request.dryRun ?? false;
      const verbose = request.verbose ?? false;

      await events.stage('stage.started', 'before-commands');
      const before = request.skipBefore
        ? emptyCommands()
        : await executePlannedCommands({
            commands: taskCommands(
              task,
              loaded.value.root,
              'before',
              dependencies.ids,
            ),
            dryRun,
            verbose,
            ...(request.signal ? { signal: request.signal } : {}),
          }, dependencies);
      for (const outcome of before.outcomes) await events.command(outcome);
      if (!before.success) {
        for (const item of before.diagnostics) await events.diagnostic(item);
        return failure(before.diagnostics);
      }
      await events.stage('stage.completed', 'before-commands', {
        itemCount: before.outcomes.length,
      });

      await events.stage('stage.started', 'plan');
      const prepared = await prepareGenerationPlan(dependencies, {
        codepotFile: loaded.value,
        task: task.name,
        ...(request.refresh === undefined ? {} : { refresh: request.refresh }),
        dryRun,
        ...(request.skipBefore === undefined
          ? {}
          : { skipBefore: request.skipBefore }),
        ...(request.skipAfter === undefined
          ? {}
          : { skipAfter: request.skipAfter }),
        ...(request.signal ? { signal: request.signal } : {}),
      });
      if (!prepared.success) {
        for (const item of prepared.diagnostics) await events.diagnostic(item);
        return prepared;
      }
      await events.stage('stage.completed', 'plan', {
        itemCount: prepared.value.plan.files.length,
      });

      await events.stage('stage.started', 'render');
      const rendered = await renderGeneration(dependencies, {
        plan: prepared.value.plan,
        templates: prepared.value.templates,
        cache: request.refresh ? 'refresh' : 'auto',
        ...(request.signal ? { signal: request.signal } : {}),
      });
      if (!rendered.success) {
        for (const item of rendered.diagnostics) await events.diagnostic(item);
        return rendered;
      }
      await events.stage('stage.completed', 'render', {
        itemCount: rendered.value.files.length,
      });

      await events.stage('stage.started', 'write');
      let managed: Awaited<ReturnType<typeof applyManagedWrite>>;
      try {
        managed = await applyManagedWrite({
          task: task.name,
          ...(task.manifest ? { configuredManifest: task.manifest } : {}),
          projectRoot: loaded.value.root,
          outputRoot: prepared.value.plan.outputRoot,
          plan: prepared.value.plan,
          rendered: rendered.value,
          dryRun,
          transactional: task.transactional,
          ...(request.signal ? { signal: request.signal } : {}),
        }, dependencies);
      } catch (caught) {
        const rollback = caught instanceof ManagedWriteError ? caught.rollback : [];
        const diagnostics = [
          diagnostic('GENERATION_MANAGED_WRITE_FAILED', caught),
          ...(rollback.length
            ? [rollbackDiagnostic(rollback.length, 'write failure or cancellation')]
            : []),
        ];
        for (const item of diagnostics) await events.diagnostic(item);
        return failure(diagnostics);
      }
      for (const outcome of managed.files) await events.file(outcome);
      await events.stage('stage.completed', 'write', {
        itemCount: managed.files.length,
      });

      await events.stage('stage.started', 'after-commands');
      const afterCommands = prepared.value.plan.commands.filter(
        (command) => command.phase === 'after',
      );
      const after = request.skipAfter
        ? emptyCommands()
        : await executePlannedCommands({
            commands: afterCommands,
            dryRun,
            verbose,
            ...(request.signal ? { signal: request.signal } : {}),
          }, dependencies);
      for (const outcome of after.outcomes) await events.command(outcome);
      if (!after.success) {
        const rollback = managed.transaction
          ? await managed.transaction.rollback()
          : [];
        const diagnostics = [
          ...after.diagnostics,
          ...(rollback.length
            ? [rollbackDiagnostic(
                rollback.length,
                'required after-command failure',
              )]
            : []),
        ];
        for (const item of diagnostics) await events.diagnostic(item);
        return failure(diagnostics);
      }
      managed.transaction?.complete();
      await events.stage('stage.completed', 'after-commands', {
        itemCount: after.outcomes.length,
      });

      const diagnostics = [
        ...prepared.diagnostics,
        ...rendered.diagnostics,
        ...before.diagnostics,
        ...managed.diagnostics,
        ...after.diagnostics,
      ];
      for (const item of diagnostics) await events.diagnostic(item);
      const commands = [...before.outcomes, ...after.outcomes];
      const report = createGenerationReport({
        task: task.name,
        status: dryRun ? 'dryRun' : 'success',
        startedAt,
        finishedAt: dependencies.clock.monotonicMilliseconds(),
        plan: prepared.value.plan,
        rendered: rendered.value,
        files: managed.files,
        commandCount: commands.length,
        diagnostics,
      });
      results.push({
        task: task.name,
        dryRun,
        plan: prepared.value.plan,
        rendered: rendered.value,
        files: managed.files,
        commands,
        cleaned: managed.cleaned,
        manifest: managed.manifest,
        report,
        rolledBack: false,
        diagnostics,
      });
    }
    return success(results, results.flatMap((result) => result.diagnostics));
  } catch (caught) {
    return failure([
      diagnostic('GENERATION_EXECUTION_CANCELLED', caught),
    ]);
  }
}

function emptyCommands(): {
  readonly success: true;
  readonly outcomes: readonly CommandExecutionOutcome[];
  readonly diagnostics: readonly Diagnostic[];
} {
  return { success: true, outcomes: [], diagnostics: [] };
}

function rollbackDiagnostic(count: number, reason: string): Diagnostic {
  return {
    code: 'GENERATION_ROLLBACK_COMPLETED',
    severity: 'info',
    layer: 'generation',
    message: `Rolled back ${count} file changes after ${reason}.`,
  };
}
