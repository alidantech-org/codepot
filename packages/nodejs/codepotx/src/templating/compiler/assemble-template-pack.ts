import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  CompiledTemplateDescriptor,
  CompiledTemplateFolder,
  CompiledTemplatePack,
  Diagnostic,
  ResolvedSource,
} from '@/contract/index';
import { CODEPOT_ARTIFACT_PRODUCER } from '@/internal/package-info';
import type { NormalizedPathsConfig } from '../config/normalized-paths-config';
import type { TemplatingDependencies } from '../templating.types';

export async function assembleTemplatePack(
  dependencies: TemplatingDependencies,
  source: ResolvedSource,
  config: NormalizedPathsConfig,
  templates: readonly CompiledTemplateDescriptor[],
  diagnostics: readonly Diagnostic[],
): Promise<CompiledTemplatePack> {
  const folders: readonly CompiledTemplateFolder[] = Object.entries(config.folders)
    .map(([name, folder]) => {
      const alias = folder.alias ?? folder.as;
      return {
        name,
        parts: folder.parts ?? [],
        mode: folder.mode ?? 'once',
        ...(folder.select ? { select: folder.select } : {}),
        ...(alias ? { alias } : {}),
        ...(folder.lifecycle ? { lifecycle: folder.lifecycle } : {}),
        ...(folder.description ? { description: folder.description } : {}),
        ...(folder.metadata ? { metadata: folder.metadata } : {}),
      };
    })
    .sort((left, right) => left.name.localeCompare(right.name));
  const orderedTemplates = [...templates].sort((left, right) =>
    left.path.localeCompare(right.path),
  );
  const body: Omit<CompiledTemplatePack, 'header'> = {
    source,
    manifest: {
      name: config.name ?? source.id,
      version: config.version,
      ...(config.description ? { description: config.description } : {}),
      templateExtension: config.templateExtension,
      stripTemplateExtension: config.stripTemplateExtension,
      allowRawFiles: config.allowRawFiles,
      includeHidden: config.includeHidden,
      ignore: [...config.ignore].sort(),
      helpers: [...new Set(config.helpers)].sort(),
      partials: orderedTemplates.flatMap((template) =>
        template.kind === 'partial' && template.partialName
          ? [template.partialName]
          : [],
      ).sort(),
      variableRequirements: config.variableRequirements,
      ...(config.metadata ? { metadata: config.metadata } : {}),
    },
    folders,
    writePolicy: {
      defaultMode: config.write.defaultMode,
      managedRoots: config.write.managedRoots,
      immutableRoots: config.write.immutableRoots,
      protectedRoots: config.write.protectedRoots,
      cleanRoots: config.write.cleanRoots,
    },
    templates: orderedTemplates,
    files: source.files,
    diagnostics,
  };
  const contentDigest = await dependencies.hashes.text(
    dependencies.data.stringifyJson(body),
  );
  return {
    header: {
      kind: 'codepot.templates',
      protocolVersion: CODEPOT_PROTOCOL_VERSION,
      artifactVersion: CODEPOT_ARTIFACT_VERSION,
      producer: CODEPOT_ARTIFACT_PRODUCER,
      contentDigest,
      sourceDigest: source.digest,
    },
    ...body,
  };
}
