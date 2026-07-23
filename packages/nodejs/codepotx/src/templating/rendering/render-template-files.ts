import type {
  TemplateRenderRequest,
  TemplateRenderResult,
  VirtualFile,
} from '@/contract/index';
import {
  caughtDiagnostic,
  failure,
  success,
} from '@/internal/results/operation-results';
import { createTemplateRenderer } from '../helpers';
import type { TemplatingDependencies } from '../templating.types';

export async function renderTemplateFiles(
  dependencies: TemplatingDependencies,
  request: TemplateRenderRequest,
): Promise<TemplateRenderResult> {
  try {
    const byId = new Map(
      request.templates.templates.map((template) => [template.id, template]),
    );
    const renderer = createTemplateRenderer(request.templates.manifest.helpers);
    for (const partial of request.templates.templates.filter(
      (template) => template.kind === 'partial',
    )) {
      if (partial.partialName) {
        renderer.registerPartial(partial.partialName, partial.text ?? '');
      }
    }
    const files: VirtualFile[] = [];
    for (const item of request.files) {
      const template = byId.get(item.templateId);
      if (!template) throw new Error(`Unknown template: ${item.templateId}`);
      if (template.kind === 'partial') {
        throw new Error(`Partial cannot be emitted directly: ${template.id}`);
      }
      const content = template.kind === 'raw'
        ? { encoding: 'base64' as const, data: template.dataBase64 ?? '' }
        : {
            encoding: 'utf8' as const,
            text: renderer.compile(
              template.text ?? '',
              { strict: true, noEscape: true },
            )(item.context, {
              allowCallsToHelperMissing: false,
              allowProtoMethodsByDefault: false,
              allowProtoPropertiesByDefault: false,
            }),
          };
      const serialized = content.encoding === 'utf8' ? content.text : content.data;
      files.push({
        id: `virtual:${item.outputPath}`,
        path: item.outputPath,
        lifecycle: template.lifecycle ?? request.templates.writePolicy.defaultMode,
        compareMode: template.compareMode,
        content,
        contentDigest: content.encoding === 'utf8'
          ? await dependencies.hashes.text(serialized)
          : await dependencies.hashes.base64(serialized),
        metadata: { templateId: template.id },
      });
    }
    return success(files);
  } catch (caught) {
    return failure([
      caughtDiagnostic('templating', 'TEMPLATING_RENDER_FAILED', caught),
    ]);
  }
}
