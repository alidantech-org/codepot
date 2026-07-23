import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  GenerationRenderRequest,
  GenerationRenderResult,
  RenderedGeneration,
} from '@/contract/index';
import { CODEPOT_ARTIFACT_PRODUCER } from '@/internal/package-info';
import type { GenerationDependencies } from '../generation.types';
import { artifactReference } from '../planning';
import {
  readRenderedGenerationCache,
  writeRenderedGenerationCache,
} from '../render-cache';
import { diagnostic, error, failure, success } from '../results';

export async function renderGeneration(
  dependencies: GenerationDependencies,
  request: GenerationRenderRequest,
): Promise<GenerationRenderResult> {
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
        dependencies,
      );
      if (cached) return success(cached, cached.diagnostics);
    }
    const rendered = await dependencies.templating.render({
      templates: request.templates,
      files: emittable.map((file) => ({
        templateId: file.templateId,
        outputPath: file.outputPath,
        context: file.context,
      })),
    });
    if (!rendered.success) return rendered;
    request.signal?.throwIfAborted();
    const body: Omit<RenderedGeneration, 'header'> = {
      plan: artifactReference(request.plan),
      files: rendered.value,
      diagnostics: rendered.diagnostics,
    };
    const contentDigest = await dependencies.hashes.text(
      dependencies.data.stringifyJson(body),
    );
    const value: RenderedGeneration = {
      header: {
        kind: 'codepot.rendered-generation',
        protocolVersion: CODEPOT_PROTOCOL_VERSION,
        artifactVersion: CODEPOT_ARTIFACT_VERSION,
        producer: CODEPOT_ARTIFACT_PRODUCER,
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
        dependencies,
      );
    }
    return success(value, rendered.diagnostics);
  } catch (caught) {
    return failure([diagnostic('GENERATION_RENDER_FAILED', caught)]);
  }
}
