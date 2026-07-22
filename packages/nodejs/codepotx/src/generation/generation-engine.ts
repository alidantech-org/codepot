import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  CodepotFileLoadRequest,
  CodepotFileLoadResult,
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
import type {
  CodepotFileInput,
  GenerationDependencies,
  GenerationEngine,
} from './generation.types';
import { compileCodepotFile, findTask } from './codepot-file';
import { artifactReference, joinPath, planClean, planCommands, planFiles } from './planning';
import { diagnostic, error, failure, success } from './results';

interface PreparedPlan {
  readonly plan: GenerationPlan;
  readonly authoring: CompiledAuthoringArtifact;
  readonly templates: CompiledTemplatePack;
}

export class DefaultGenerationEngine implements GenerationEngine {
  readonly #dependencies: GenerationDependencies;

  constructor(dependencies: GenerationDependencies) {
    this.#dependencies = dependencies;
  }

  async load(request: CodepotFileLoadRequest): Promise<CodepotFileLoadResult> {
    try {
      const located = await this.#locateCodepotFile(request);
      const input = this.#dependencies.data.parseYaml<CodepotFileInput>(await this.#dependencies.files.readText(located.path));
      const compiled = compileCodepotFile(input, located.path, located.root);
      if (!compiled.allow) {
        return failure([error('GENERATION_NOT_ALLOWED', `${located.path} must explicitly set allow: true.`)]);
      }
      return success(compiled);
    } catch (caught) {
      return failure([diagnostic('GENERATION_CODEPOT_FILE_LOAD_FAILED', caught)]);
    }
  }

  async plan(request: GenerationPlanRequest): Promise<GenerationPlanResult> {
    const prepared = await this.#preparePlan(request);
    return prepared.success ? success(prepared.value.plan, prepared.diagnostics) : prepared;
  }

  async render(request: GenerationRenderRequest): Promise<GenerationRenderResult> {
    const rendered = await this.#dependencies.templating.render({
      templates: request.templates,
      files: request.plan.files
        .filter((file) => !file.refusalReason)
        .map((file) => ({ templateId: file.templateId, outputPath: file.outputPath, context: file.context })),
    });
    if (!rendered.success) return rendered;
    const body = { plan: artifactReference(request.plan), files: rendered.value, diagnostics: rendered.diagnostics };
    const contentDigest = await this.#dependencies.hashes.text(this.#dependencies.data.stringifyJson(body));
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
    return success(value, rendered.diagnostics);
  }

  async write(request: GenerationWriteRequest): Promise<GenerationWriteResult> {
    try {
      const files = request.rendered.files.map((file) => ({ ...file, path: joinPath(request.outputRoot, file.path) }));
      return success(await this.#dependencies.writer.writeBatch({
        files,
        root: request.outputRoot,
        atomic: request.atomic ?? true,
        dryRun: request.dryRun ?? false,
      }));
    } catch (caught) {
      return failure([diagnostic('GENERATION_WRITE_FAILED', caught)]);
    }
  }

  async clean(request: GenerationCleanRequest): Promise<GenerationCleanResult> {
    try {
      const cleaned: PortablePath[] = [];
      for (const item of request.plan.clean) {
        if (!item.allowed) continue;
        if (!request.dryRun) await this.#dependencies.files.remove(item.path, { recursive: true, force: true });
        cleaned.push(item.path);
      }
      return success(cleaned);
    } catch (caught) {
      return failure([diagnostic('GENERATION_CLEAN_FAILED', caught)]);
    }
  }

  async runCommands(request: GenerationCommandRequest): Promise<GenerationCommandResult> {
    try {
      const commands = request.plan.commands.filter((command) => command.phase === request.phase);
      const outcomes: CommandExecutionOutcome[] = [];
      for (const command of commands) {
        const result = await this.#dependencies.commands.run({
          command: command.command,
          cwd: command.cwd,
          environment: command.environment,
          optional: command.optional,
          ...(request.dryRun === undefined ? {} : { dryRun: request.dryRun }),
          ...(request.verbose === undefined ? {} : { verbose: request.verbose }),
        });
        outcomes.push({
          id: command.id,
          phase: command.phase,
          command: command.command,
          cwd: command.cwd,
          exitCode: result.exitCode,
          skipped: result.skipped,
          optional: command.optional,
          stdout: result.stdout,
          stderr: result.stderr,
        });
        if (!command.optional && !result.skipped && result.exitCode !== 0) {
          return failure([error('GENERATION_COMMAND_FAILED', `Command failed: ${command.command}`)]);
        }
      }
      return success(outcomes);
    } catch (caught) {
      return failure([diagnostic('GENERATION_COMMAND_FAILED', caught)]);
    }
  }

  async execute(request: GenerationExecuteRequest): Promise<GenerationExecuteResult> {
    const loaded = await this.load(request.codepotFile ?? {});
    if (!loaded.success) return loaded;
    const tasks = request.allTasks
      ? loaded.value.tasks
      : [findTask(loaded.value, request.task)];
    const results: GenerationResult[] = [];
    for (const task of tasks) {
      const prepared = await this.#preparePlan({
        codepotFile: loaded.value,
        task: task.name,
        ...(request.refresh === undefined ? {} : { refresh: request.refresh }),
        ...(request.dryRun === undefined ? {} : { dryRun: request.dryRun }),
        ...(request.skipBefore === undefined ? {} : { skipBefore: request.skipBefore }),
        ...(request.skipAfter === undefined ? {} : { skipAfter: request.skipAfter }),
      });
      if (!prepared.success) return prepared;
      const before = request.skipBefore ? success<readonly CommandExecutionOutcome[]>([]) : await this.runCommands({ plan: prepared.value.plan, phase: 'before', ...(request.dryRun === undefined ? {} : { dryRun: request.dryRun }), ...(request.verbose === undefined ? {} : { verbose: request.verbose }) });
      if (!before.success) return before;
      const cleaned = await this.clean({ plan: prepared.value.plan, ...(request.dryRun === undefined ? {} : { dryRun: request.dryRun }) });
      if (!cleaned.success) return cleaned;
      const rendered = await this.render({ plan: prepared.value.plan, templates: prepared.value.templates });
      if (!rendered.success) return rendered;
      const written = await this.write({ rendered: rendered.value, outputRoot: prepared.value.plan.outputRoot, ...(request.dryRun === undefined ? {} : { dryRun: request.dryRun }), atomic: true });
      if (!written.success) return written;
      const after = request.skipAfter ? success<readonly CommandExecutionOutcome[]>([]) : await this.runCommands({ plan: prepared.value.plan, phase: 'after', ...(request.dryRun === undefined ? {} : { dryRun: request.dryRun }), ...(request.verbose === undefined ? {} : { verbose: request.verbose }) });
      if (!after.success) return after;
      results.push({
        task: task.name,
        dryRun: request.dryRun ?? false,
        plan: prepared.value.plan,
        rendered: rendered.value,
        files: written.value,
        commands: [...before.value, ...after.value],
        cleaned: cleaned.value,
        diagnostics: [...prepared.diagnostics, ...rendered.diagnostics, ...written.diagnostics],
      });
    }
    return success(results, results.flatMap((result) => result.diagnostics));
  }

  async #preparePlan(request: GenerationPlanRequest): Promise<
    | { readonly success: true; readonly value: PreparedPlan; readonly diagnostics: readonly Diagnostic[] }
    | { readonly success: false; readonly diagnostics: readonly Diagnostic[] }
  > {
    try {
      const task = findTask(request.codepotFile, request.task);
      const authoringResult = request.authoring
        ? success(request.authoring)
        : await this.#dependencies.authoring.compile({
            source: task.authoring,
            projectRoot: request.codepotFile.root,
            cache: request.refresh ? 'refresh' : 'auto',
          });
      if (!authoringResult.success) return authoringResult;
      const templateResult = request.templates
        ? success(request.templates)
        : await this.#dependencies.templating.compile({
            source: task.templates,
            projectRoot: request.codepotFile.root,
            cache: request.refresh ? 'refresh' : 'auto',
          });
      if (!templateResult.success) return templateResult;
      const contextResult = await this.#dependencies.templating.createContext({
        authoring: authoringResult.value,
        templates: templateResult.value,
        project: request.codepotFile.defaults,
        ...(task.variables ? { variables: task.variables } : {}),
        ...(task.frontend ? { selectedFrontend: task.frontend } : {}),
      });
      if (!contextResult.success) return contextResult;
      const diagnostics: Diagnostic[] = [
        ...authoringResult.diagnostics,
        ...templateResult.diagnostics,
        ...contextResult.diagnostics,
      ];
      const files = planFiles(templateResult.value, contextResult.value, diagnostics);
      const commands = planCommands(task, request.codepotFile.root, request.skipBefore, request.skipAfter, this.#dependencies.ids);
      const outputRoot = joinPath(request.codepotFile.root, task.output);
      const clean = planClean(task, outputRoot, templateResult.value, this.#dependencies.ids);
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
      };
      const contentDigest = await this.#dependencies.hashes.text(this.#dependencies.data.stringifyJson(body));
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
      return success({ plan, authoring: authoringResult.value, templates: templateResult.value }, diagnostics);
    } catch (caught) {
      return failure([diagnostic('GENERATION_PLAN_FAILED', caught)]);
    }
  }

  async #locateCodepotFile(request: CodepotFileLoadRequest): Promise<{ readonly path: string; readonly root: string }> {
    if (request.source) {
      const resolved = await this.#dependencies.sources.resolve(request.source, request.projectRoot ? { projectRoot: request.projectRoot } : {});
      return { path: request.file ? joinPath(resolved.root, request.file) : resolved.entry, root: resolved.root };
    }
    const root = request.projectRoot ?? '.';
    return { path: joinPath(root, request.file ?? 'CodepotFile.yml'), root };
  }
}

export function createGenerationEngine(dependencies: GenerationDependencies): GenerationEngine {
  return new DefaultGenerationEngine(dependencies);
}
