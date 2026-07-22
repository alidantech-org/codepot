import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  CodepotFileLoadRequest,
  CodepotFileLoadResult,
  CodepotTaskConfig,
  CommandExecutionOutcome,
  CompiledAuthoringArtifact,
  CompiledTemplatePack,
  Diagnostic,
  GenerationCleanRequest,
  GenerationCleanResult,
  GenerationCommandRequest,
  GenerationCommandResult,
  GenerationExecuteRequest,
  GenerationExecuteResult,
  GenerationPlan,
  GenerationPlanRequest,
  GenerationPlanResult,
  GenerationRenderRequest,
  GenerationRenderResult,
  GenerationResult,
  GenerationWriteRequest,
  GenerationWriteResult,
  PortablePath,
  RenderedGeneration,
} from '@/contract/index';

import { compileCodepotFile, findTask } from './codepot-file';
import { executePlannedCommands, taskCommands } from './command-execution';
import { GenerationEventPublisher } from './generation-events';
import type {
  CodepotFileInput,
  GenerationDependencies,
  GenerationEngine,
} from './generation.types';
import { applyManagedWrite, ManagedWriteError } from './managed-write';
import {
  artifactReference,
  joinPath,
  planClean,
  planCommands,
  planFiles,
} from './planning';
import {
  readRenderedGenerationCache,
  writeRenderedGenerationCache,
} from './render-cache';
import { createGenerationReport } from './report';
import { diagnostic, error, failure, success } from './results';

interface PreparedPlan {
  readonly plan: GenerationPlan;
  readonly authoring: CompiledAuthoringArtifact;
  readonly templates: CompiledTemplatePack;
  readonly task: CodepotTaskConfig;
}

/**
 * Production orchestration engine. Authoring and templating are accessed only
 * through ports; all file mutation happens after a complete validated render.
 */
export class DefaultGenerationEngine implements GenerationEngine {
  readonly #dependencies: GenerationDependencies;

  constructor(dependencies: GenerationDependencies) {
    this.#dependencies = dependencies;
  }

  async load(request: CodepotFileLoadRequest): Promise<CodepotFileLoadResult> {
    try {
      const located = await this.#locateCodepotFile(request);
      const input = this.#dependencies.data.parseYaml<CodepotFileInput>(
        await this.#dependencies.files.readText(located.path),
      );
      const compiled = compileCodepotFile(input, located.path, located.root);
      if (!compiled.allow) {
        return failure([error(
          'GENERATION_NOT_ALLOWED',
          `${located.path} must explicitly set allow: true.`,
        )]);
      }
      return success(compiled);
    } catch (caught) {
      return failure([diagnostic('GENERATION_CODEPOT_FILE_LOAD_FAILED', caught)]);
    }
  }

  async plan(request: GenerationPlanRequest): Promise<GenerationPlanResult> {
    try {
      request.signal?.throwIfAborted();
      const prepared = await this.#preparePlan(request);
      request.signal?.throwIfAborted();
      return prepared.success
        ? success(prepared.value.plan, prepared.diagnostics)
        : prepared;
    } catch (caught) {
      return failure([diagnostic('GENERATION_PLAN_CANCELLED', caught)]);
    }
  }

  async render(request: GenerationRenderRequest): Promise<GenerationRenderResult> {
    try {
      request.signal?.throwIfAborted();
      const emittable = request.plan.files.filter((file) => !file.refusalReason);
      if (emittable.length !== request.plan.files.length) {
        return failure([error(
          'GENERATION_REFUSED_FILES',
          'Generation plan contains refused files and cannot be rendered.',
        )]);
      }
      if (request.cache !== 'bypass' && request.cache !== 'refresh') {
        const cached = await readRenderedGenerationCache(
          request.plan,
          request.templates,
          this.#dependencies,
        );
        if (cached) return success(cached, cached.diagnostics);
      }
      const rendered = await this.#dependencies.templating.render({
        templates: request.templates,
        files: emittable.map((file) => ({
          templateId: file.templateId,
          outputPath: file.outputPath,
          context: file.context,
        })),
      });
      if (!rendered.success) return rendered;
      request.signal?.throwIfAborted();
      const body = {
        plan: artifactReference(request.plan),
        files: rendered.value,
        diagnostics: rendered.diagnostics,
      } as const;
      const contentDigest = await this.#dependencies.hashes.text(
        this.#dependencies.data.stringifyJson(body),
      );
      const value: RenderedGeneration = {
        header: {
          kind: 'codepot.rendered-generation',
          protocolVersion: CODEPOT_PROTOCOL_VERSION,
          artifactVersion: CODEPOT_ARTIFACT_VERSION,
          producer: { name: 'codepotx', version: '0.0.0' },
          contentDigest,
          sourceDigest: request.plan.header.contentDigest,
        },
        ...body,
      };
      if (request.cache !== 'bypass') {
        await writeRenderedGenerationCache(
          request.plan,
          request.templates,
          value,
          this.#dependencies,
        );
      }
      return success(value, rendered.diagnostics);
    } catch (caught) {
      return failure([diagnostic('GENERATION_RENDER_FAILED', caught)]);
    }
  }

  async write(request: GenerationWriteRequest): Promise<GenerationWriteResult> {
    try {
      request.signal?.throwIfAborted();
      const files = request.rendered.files.map((file) => ({
        ...file,
        path: joinPath(request.outputRoot, file.path),
      }));
      const outcomes = await this.#dependencies.writer.writeBatch({
        files,
        root: request.outputRoot,
        atomic: request.atomic ?? true,
        dryRun: request.dryRun ?? false,
      });
      request.signal?.throwIfAborted();
      return success(outcomes);
    } catch (caught) {
      return failure([diagnostic('GENERATION_WRITE_FAILED', caught)]);
    }
  }

  /** Direct clean calls refuse recursive directories; task cleanup uses manifests. */
  async clean(request: GenerationCleanRequest): Promise<GenerationCleanResult> {
    try {
      const cleaned: PortablePath[] = [];
      const diagnostics: Diagnostic[] = [];
      for (const item of request.plan.clean) {
        request.signal?.throwIfAborted();
        if (!item.allowed || !await this.#dependencies.files.exists(item.path)) continue;
        const stat = await this.#dependencies.files.stat(item.path);
        if (stat.kind !== 'file') {
          diagnostics.push(error(
            'GENERATION_BROAD_CLEAN_REFUSED',
            `Refusing recursive directory cleanup without a managed manifest: ${item.path}`,
          ));
          continue;
        }
        if (!request.dryRun) await this.#dependencies.files.remove(item.path, { force: true });
        cleaned.push(item.path);
      }
      return diagnostics.some((item) => item.severity === 'error')
        ? failure(diagnostics)
        : success(cleaned, diagnostics);
    } catch (caught) {
      return failure([diagnostic('GENERATION_CLEAN_FAILED', caught)]);
    }
  }

  async runCommands(request: GenerationCommandRequest): Promise<GenerationCommandResult> {
    try {
      const result = await executePlannedCommands({
        commands: request.plan.commands.filter((command) => command.phase === request.phase),
        dryRun: request.dryRun ?? false,
        verbose: request.verbose ?? false,
        ...(request.signal ? { signal: request.signal } : {}),
      }, this.#dependencies);
      return result.success
        ? success(result.outcomes, result.diagnostics)
        : failure(result.diagnostics);
    } catch (caught) {
      return failure([diagnostic('GENERATION_COMMAND_FAILED', caught)]);
    }
  }

  async execute(request: GenerationExecuteRequest): Promise<GenerationExecuteResult> {
    try {
      request.signal?.throwIfAborted();
      const loaded = await this.load(request.codepotFile ?? {});
      if (!loaded.success) return loaded;
      let tasks: readonly CodepotTaskConfig[];
      try {
        tasks = request.allTasks
          ? loaded.value.tasks
          : [findTask(loaded.value, request.task)];
      } catch (caught) {
        return failure([diagnostic('GENERATION_TASK_SELECTION_FAILED', caught)]);
      }

      const results: GenerationResult[] = [];
      for (const task of tasks) {
        request.signal?.throwIfAborted();
        const events = new GenerationEventPublisher(this.#dependencies);
        const startedAt = this.#dependencies.clock.monotonicMilliseconds();
        const dryRun = request.dryRun ?? false;
        const verbose = request.verbose ?? false;

        await events.stage('stage.started', 'before-commands');
        const before = request.skipBefore
          ? emptyCommands()
          : await executePlannedCommands({
              commands: taskCommands(task, loaded.value.root, 'before', this.#dependencies.ids),
              dryRun,
              verbose,
              ...(request.signal ? { signal: request.signal } : {}),
            }, this.#dependencies);
        for (const outcome of before.outcomes) await events.command(outcome);
        if (!before.success) {
          for (const item of before.diagnostics) await events.diagnostic(item);
          return failure(before.diagnostics);
        }
        await events.stage('stage.completed', 'before-commands', { itemCount: before.outcomes.length });

        await events.stage('stage.started', 'plan');
        const prepared = await this.#preparePlan({
          codepotFile: loaded.value,
          task: task.name,
          ...(request.refresh === undefined ? {} : { refresh: request.refresh }),
          dryRun,
          ...(request.skipBefore === undefined ? {} : { skipBefore: request.skipBefore }),
          ...(request.skipAfter === undefined ? {} : { skipAfter: request.skipAfter }),
          ...(request.signal ? { signal: request.signal } : {}),
        });
        if (!prepared.success) {
          for (const item of prepared.diagnostics) await events.diagnostic(item);
          return prepared;
        }
        await events.stage('stage.completed', 'plan', { itemCount: prepared.value.plan.files.length });

        await events.stage('stage.started', 'render');
        const rendered = await this.render({
          plan: prepared.value.plan,
          templates: prepared.value.templates,
          cache: request.refresh ? 'refresh' : 'auto',
          ...(request.signal ? { signal: request.signal } : {}),
        });
        if (!rendered.success) {
          for (const item of rendered.diagnostics) await events.diagnostic(item);
          return rendered;
        }
        await events.stage('stage.completed', 'render', { itemCount: rendered.value.files.length });

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
          }, this.#dependencies);
        } catch (caught) {
          const rollback = caught instanceof ManagedWriteError ? caught.rollback : [];
          const diagnostics = [
            diagnostic('GENERATION_MANAGED_WRITE_FAILED', caught),
            ...(rollback.length ? [rollbackDiagnostic(rollback.length, 'write failure or cancellation')] : []),
          ];
          for (const item of diagnostics) await events.diagnostic(item);
          return failure(diagnostics);
        }
        for (const outcome of managed.files) await events.file(outcome);
        await events.stage('stage.completed', 'write', { itemCount: managed.files.length });

        await events.stage('stage.started', 'after-commands');
        const afterCommands = prepared.value.plan.commands.filter((command) => command.phase === 'after');
        const after = request.skipAfter
          ? emptyCommands()
          : await executePlannedCommands({
              commands: afterCommands,
              dryRun,
              verbose,
              ...(request.signal ? { signal: request.signal } : {}),
            }, this.#dependencies);
        for (const outcome of after.outcomes) await events.command(outcome);
        if (!after.success) {
          const rollback = managed.transaction ? await managed.transaction.rollback() : [];
          const diagnostics = [
            ...after.diagnostics,
            ...(rollback.length ? [rollbackDiagnostic(rollback.length, 'required after-command failure')] : []),
          ];
          for (const item of diagnostics) await events.diagnostic(item);
          return failure(diagnostics);
        }
        managed.transaction?.complete();
        await events.stage('stage.completed', 'after-commands', { itemCount: after.outcomes.length });

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
          finishedAt: this.#dependencies.clock.monotonicMilliseconds(),
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
      return failure([diagnostic('GENERATION_EXECUTION_CANCELLED', caught)]);
    }
  }

  async #preparePlan(request: GenerationPlanRequest): Promise<
    | { readonly success: true; readonly value: PreparedPlan; readonly diagnostics: readonly Diagnostic[] }
    | { readonly success: false; readonly diagnostics: readonly Diagnostic[] }
  > {
    try {
      request.signal?.throwIfAborted();
      const task = findTask(request.codepotFile, request.task);
      const authoringResult = request.authoring
        ? success(request.authoring)
        : await this.#dependencies.authoring.compile({
            source: task.authoring,
            projectRoot: request.codepotFile.root,
            cache: request.refresh ? 'refresh' : 'auto',
          });
      if (!authoringResult.success) return authoringResult;
      request.signal?.throwIfAborted();
      const templateResult = request.templates
        ? success(request.templates)
        : await this.#dependencies.templating.compile({
            source: task.templates,
            projectRoot: request.codepotFile.root,
            cache: request.refresh ? 'refresh' : 'auto',
          });
      if (!templateResult.success) return templateResult;
      request.signal?.throwIfAborted();
      const contextRequest = {
        authoring: authoringResult.value,
        templates: templateResult.value,
        project: request.codepotFile.defaults,
        ...(task.variables ? { variables: task.variables } : {}),
        ...(task.frontend ? { selectedFrontend: task.frontend } : {}),
      } as const;
      const contextResult = await this.#dependencies.templating.createContext(contextRequest);
      if (!contextResult.success) return contextResult;
      const validation = await this.#dependencies.templating.validateContext({
        ...contextRequest,
        strict: true,
      });
      if (!validation.success) return validation;
      request.signal?.throwIfAborted();

      const diagnostics: Diagnostic[] = [
        ...authoringResult.diagnostics,
        ...templateResult.diagnostics,
        ...contextResult.diagnostics,
        ...validation.diagnostics,
      ];
      const files = planFiles(templateResult.value, contextResult.value, diagnostics, {
        imports: this.#dependencies.imports,
      });
      const commands = planCommands(
        task,
        request.codepotFile.root,
        request.skipBefore,
        request.skipAfter,
      );
      const outputRoot = joinPath(request.codepotFile.root, task.output);
      const clean = planClean(task, outputRoot, templateResult.value);
      const body = {
        task: task.name,
        projectRoot: request.codepotFile.root,
        outputRoot,
        authoring: artifactReference(authoringResult.value),
        templates: artifactReference(templateResult.value),
        files,
        commands,
        clean,
        diagnostics,
      } as const;
      if (
        diagnostics.some((item) => item.severity === 'error')
        || files.some((file) => file.refusalReason)
      ) {
        return failure(diagnostics.length ? diagnostics : [error(
          'GENERATION_PLAN_REFUSED',
          'Generation plan contains refused files.',
        )]);
      }
      const contentDigest = await this.#dependencies.hashes.text(
        this.#dependencies.data.stringifyJson(body),
      );
      const plan: GenerationPlan = {
        header: {
          kind: 'codepot.generation-plan',
          protocolVersion: CODEPOT_PROTOCOL_VERSION,
          artifactVersion: CODEPOT_ARTIFACT_VERSION,
          producer: { name: 'codepotx', version: '0.0.0' },
          contentDigest,
          sourceDigest: await this.#dependencies.hashes.values([
            authoringResult.value.header.contentDigest,
            templateResult.value.header.contentDigest,
          ]),
        },
        ...body,
      };
      return success({
        plan,
        authoring: authoringResult.value,
        templates: templateResult.value,
        task,
      }, diagnostics);
    } catch (caught) {
      return failure([diagnostic('GENERATION_PLAN_FAILED', caught)]);
    }
  }

  async #locateCodepotFile(
    request: CodepotFileLoadRequest,
  ): Promise<{ readonly path: string; readonly root: string }> {
    if (request.source) {
      const resolved = await this.#dependencies.sources.resolve(
        request.source,
        request.projectRoot ? { projectRoot: request.projectRoot } : {},
      );
      return {
        path: request.file ? joinPath(resolved.root, request.file) : resolved.entry,
        root: resolved.root,
      };
    }
    const root = request.projectRoot ?? '.';
    return { path: joinPath(root, request.file ?? 'CodepotFile.yml'), root };
  }
}

export function createGenerationEngine(dependencies: GenerationDependencies): GenerationEngine {
  return new DefaultGenerationEngine(dependencies);
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
