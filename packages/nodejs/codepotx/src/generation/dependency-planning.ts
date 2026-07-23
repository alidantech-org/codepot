import type {
  Diagnostic,
  JsonObject,
  JsonValue,
  PlannedDependency,
  PlannedFile,
} from '@/contract/index';

import { createRelativeImportAdapter } from './imports';
import type { GenerationDependencies } from './generation.types';
import {
  buildOutputIndex,
  dependencyRefs,
  findOutputByRef,
} from './output-index';

export function resolvePlannedFileDependencies(
  candidates: readonly PlannedFile[],
  diagnostics: Diagnostic[],
  adapter?: GenerationDependencies['imports'],
): PlannedFile[] {
  const files = candidates.map((file) => ({ ...file }));
  refuseDuplicatePaths(files, diagnostics);
  const outputIndex = buildOutputIndex(files);
  const imports = adapter ?? createRelativeImportAdapter();
  return files.map((file) => {
    if (file.refusalReason) return file;
    const resolved = resolveDependencies(file, outputIndex, imports, diagnostics);
    return {
      ...file,
      dependencies: resolved.dependencies,
      context: attachDependencyContext(file.context, resolved.dependencies, resolved.imports),
      ...(resolved.refusalReason ? { refusalReason: resolved.refusalReason } : {}),
    };
  });
}

function resolveDependencies(
  file: PlannedFile,
  outputIndex: ReturnType<typeof buildOutputIndex>,
  imports: NonNullable<GenerationDependencies['imports']>,
  diagnostics: Diagnostic[],
): {
  readonly dependencies: readonly PlannedDependency[];
  readonly imports: readonly JsonObject[];
  readonly refusalReason?: string;
} {
  const planned: PlannedDependency[] = [];
  const importFacts: JsonObject[] = [];
  let refusalReason: string | undefined;
  for (const ref of dependencyRefs(file.context)) {
    const targets = findOutputByRef(outputIndex, ref)
      .filter((target) => target.plannedFileId !== file.id);
    if (targets.length === 0) {
      diagnostics.push({
        code: 'GENERATION_DEPENDENCY_NOT_EMITTED',
        severity: 'warning',
        layer: 'generation',
        message: `Dependency ${ref} used by ${file.outputPath} is not emitted by this template pack.`,
        details: { ref, outputPath: file.outputPath },
      });
      planned.push({ ref, purpose: 'reference', targetRef: ref });
      continue;
    }
    if (targets.length > 1) {
      refusalReason = `Dependency ${ref} has multiple output targets.`;
      diagnostics.push({
        code: 'GENERATION_DEPENDENCY_AMBIGUOUS',
        severity: 'error',
        layer: 'generation',
        message: `${refusalReason} ${targets.map((item) => item.outputPath).join(', ')}`,
        details: {
          ref,
          outputPath: file.outputPath,
          targets: targets.map((item) => item.outputPath),
        },
      });
      continue;
    }
    const target = targets[0]!;
    const dependency: PlannedDependency = {
      ref,
      purpose: 'reference',
      targetRef: ref,
      outputPath: target.outputPath,
    };
    const resolved = imports.resolve({
      fromPath: file.outputPath,
      toPath: target.outputPath,
      dependency,
      context: file.context,
    });
    planned.push({
      ...dependency,
      importPath: resolved.importPath,
      ...(resolved.metadata ? { metadata: resolved.metadata } : {}),
    });
    importFacts.push({
      ref,
      purpose: dependency.purpose,
      outputPath: target.outputPath,
      importPath: resolved.importPath,
      ...(resolved.statement ? { statement: resolved.statement } : {}),
      ...(resolved.symbols ? { symbols: resolved.symbols } : {}),
    });
  }
  return {
    dependencies: planned.sort((left, right) => left.ref.localeCompare(right.ref)),
    imports: importFacts.sort((left, right) =>
      String(left['importPath']).localeCompare(String(right['importPath'])),
    ),
    ...(refusalReason ? { refusalReason } : {}),
  };
}

function attachDependencyContext(
  context: JsonObject,
  dependencies: readonly PlannedDependency[],
  imports: readonly JsonObject[],
): JsonObject {
  const file = asObject(context['file']) ?? {};
  const next: Record<string, JsonValue> = {
    ...context,
    dependencies: dependencies as unknown as JsonValue,
    imports,
    file: {
      ...file,
      dependencies: dependencies as unknown as JsonValue,
      imports,
    },
  };
  for (const alias of [
    'model', 'dto', 'enum', 'schema', 'entity', 'operation', 'resource', 'frontend',
  ]) {
    const selected = asObject(next[alias]);
    if (!selected) continue;
    next[alias] = {
      ...selected,
      emit: {
        ...(asObject(selected['emit']) ?? {}),
        dependencies: dependencies as unknown as JsonValue,
        imports,
      },
    };
  }
  return next;
}

function refuseDuplicatePaths(files: PlannedFile[], diagnostics: Diagnostic[]): void {
  const byPath = new Map<string, PlannedFile[]>();
  for (const file of files) {
    const selected = byPath.get(file.outputPath) ?? [];
    selected.push(file);
    byPath.set(file.outputPath, selected);
  }
  for (const [path, collisions] of byPath) {
    if (collisions.length < 2) continue;
    const reason = `Multiple templates planned the same output path: ${path}`;
    diagnostics.push({
      code: 'GENERATION_DUPLICATE_OUTPUT_PATH',
      severity: 'error',
      layer: 'generation',
      message: reason,
      details: { path, templates: collisions.map((file) => file.templateId) },
    });
    for (const collision of collisions) {
      const index = files.indexOf(collision);
      files[index] = { ...collision, refusalReason: reason };
    }
  }
}

function asObject(value: JsonValue | undefined): JsonObject | undefined {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? value as JsonObject
    : undefined;
}
