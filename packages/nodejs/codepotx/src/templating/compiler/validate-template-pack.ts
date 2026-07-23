import type {
  CompiledTemplateDescriptor,
  Diagnostic,
} from '@/contract/index';
import type { NormalizedPathsConfig } from '../config/normalized-paths-config';

export function validateCompiledTemplatePack(
  config: NormalizedPathsConfig,
  templates: readonly CompiledTemplateDescriptor[],
): readonly Diagnostic[] {
  const diagnostics: Diagnostic[] = [];
  const partials = new Map<string, string>();
  for (const template of templates) {
    if (template.kind !== 'partial' || !template.partialName) continue;
    const existing = partials.get(template.partialName);
    if (existing) {
      diagnostics.push({
        code: 'TEMPLATING_DUPLICATE_PARTIAL',
        severity: 'error',
        layer: 'templating',
        message: `Partial "${template.partialName}" is defined by both ${existing} and ${template.path}.`,
      });
    } else {
      partials.set(template.partialName, template.path);
    }
  }
  for (const name of Object.keys(config.folders)) {
    if (!templates.some((template) => template.group === name)) {
      diagnostics.push({
        code: 'TEMPLATING_FOLDER_WITHOUT_FILES',
        severity: 'warning',
        layer: 'templating',
        message: `Configured template folder "${name}" has no matching {${name}} files.`,
      });
    }
  }
  if (!templates.some((template) => template.kind !== 'partial')) {
    diagnostics.push({
      code: 'TEMPLATING_NO_EMITTABLE_FILES',
      severity: 'warning',
      layer: 'templating',
      message: 'Template pack contains no emittable templates or raw files.',
    });
  }
  return diagnostics;
}
