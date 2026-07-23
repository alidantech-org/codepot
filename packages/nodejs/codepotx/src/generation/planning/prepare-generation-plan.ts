import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  CodepotTaskConfig,
  CompiledAuthoringArtifact,
  CompiledTemplatePack,
  Diagnostic,
  GenerationPlan,
  GenerationPlanRequest,
  OperationResult,
} from '@/contract/index';
import { CODEPOT_ARTIFACT_PRODUCER } from '@/internal/package-info';
import { findTask } from '../codepot-file';
import type { GenerationDependencies } from '../generation.types';
import {
  artifactReference,
  joinPath,
  planClean,
  planCommands,
  planFiles,
} from '../planning';
import { diagnostic, error, failure, success } from '../results';

export interface PreparedGenerationPlan {
  readonly plan: GenerationPlan;
  readonly authoring: CompiledAuthoringArtifact;
  readonly templates: CompiledTemplatePack;
  readonly task: CodepotTaskConfig;
}

export async function prepareGenerationPlan(
  dependencies: GenerationDependencies,
  request: GenerationPlanRequest,
): Promise<OperationResult<PreparedGenerationPlan>> {
  try {
    request.signal?.throwIfAborted();
    const task = findTask(request.codepotFile, request.task);
    const authoringResult = request.authoring
      ? success(request.authoring)
      : await dependencies.authoring.compile({
          source: task.authoring,
          projectRoot: request.codepotFile.root,
          cache: request.refresh ? 'refresh' : 'auto',
        });
    if (!authoringResult.success) return authoringResult;
    request.signal?.throwIfAborted();

    const templateResult = request.templates
      ? success(request.templates)
      : await dependencies.templating.compile({
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
    const contextResult = await dependencies.templating.createContext(contextRequest);
    if (!contextResult.success) return contextResult;
    const validation = await dependencies.templating.validateContext({
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
    const files = planFiles(
      templateResult.value,
      contextResult.value,
      diagnostics,
      { imports: dependencies.imports },
    );
    const commands = planCommands(
      task,
      request.codepotFile.root,
      request.skipBefore,
      request.skipAfter,
    );
    const outputRoot = joinPath(request.codepotFile.root, task.output);
    const clean = planClean(task, outputRoot, templateResult.value);
    const body: Omit<GenerationPlan, 'header'> = {
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
    if (
      diagnostics.some((item) => item.severity === 'error')
      || files.some((file) => file.refusalReason)
    ) {
      return failure(
        diagnostics.length
          ? diagnostics
          : [error(
              'GENERATION_PLAN_REFUSED',
              'Generation plan contains refused files.',
            )],
      );
    }
    const contentDigest = await dependencies.hashes.text(
      dependencies.data.stringifyJson(body),
    );
    const plan: GenerationPlan = {
      header: {
        kind: 'codepot.generation-plan',
        protocolVersion: CODEPOT_PROTOCOL_VERSION,
        artifactVersion: CODEPOT_ARTIFACT_VERSION,
        producer: CODEPOT_ARTIFACT_PRODUCER,
        contentDigest,
        sourceDigest: await dependencies.hashes.values([
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
