import type { JsonObject, PlannedFile, PortablePath } from '@/contract/index';

export interface OutputIndexEntry {
  readonly ref: string;
  readonly outputPath: PortablePath;
  readonly plannedFileId: string;
  readonly templateId: string;
  readonly group: string;
}

/**
 * The output index is built before rendering. It lets dependency planners map a
 * semantic authoring reference to its generated file without framework rules.
 */
export interface GenerationOutputIndex {
  readonly entries: readonly OutputIndexEntry[];
  readonly byRef: ReadonlyMap<string, readonly OutputIndexEntry[]>;
  readonly byPath: ReadonlyMap<PortablePath, readonly OutputIndexEntry[]>;
}

export function buildOutputIndex(files: readonly PlannedFile[]): GenerationOutputIndex {
  const entries = files
    .flatMap((file) => subjectRefs(file.context).map((ref) => ({
      ref,
      outputPath: normalizePath(file.outputPath),
      plannedFileId: file.id,
      templateId: file.templateId,
      group: file.group,
    })))
    .sort((left, right) => left.ref.localeCompare(right.ref) || left.outputPath.localeCompare(right.outputPath));
  return {
    entries,
    byRef: groupBy(entries, (entry) => entry.ref),
    byPath: groupBy(entries, (entry) => entry.outputPath),
  };
}

export function findOutputByRef(
  index: GenerationOutputIndex,
  ref: string,
): readonly OutputIndexEntry[] {
  return index.byRef.get(ref) ?? [];
}

export function subjectRefs(context: JsonObject): readonly string[] {
  const output = new Set<string>();
  for (const candidate of [
    context.model,
    context.dto,
    context.enum,
    context.schema,
    context.entity,
    context.operation,
    context.resource,
    context.frontend,
  ]) {
    collectCandidateRef(candidate, output);
  }
  const file = asObject(context.file);
  if (typeof file?.subjectRef === 'string') output.add(file.subjectRef);
  if (Array.isArray(file?.subjectRefs)) {
    for (const ref of file.subjectRefs) if (typeof ref === 'string') output.add(ref);
  }
  return [...output].sort();
}

export function dependencyRefs(context: JsonObject): readonly string[] {
  const output = new Set<string>();
  const visitCandidate = (candidate: unknown): void => {
    const item = asObject(candidate);
    if (!item) return;
    const meta = asObject(item.meta);
    const emit = asObject(item.emit);
    for (const value of [meta?.dependencyRefs, meta?.dependency_refs, emit?.dependencyRefs, emit?.dependency_refs]) {
      if (!Array.isArray(value)) continue;
      for (const ref of value) if (typeof ref === 'string') output.add(ref);
    }
  };
  for (const key of ['model', 'dto', 'enum', 'schema', 'entity', 'operation', 'resource', 'frontend']) {
    visitCandidate(context[key]);
  }
  return [...output].sort();
}

function collectCandidateRef(value: unknown, output: Set<string>): void {
  const item = asObject(value);
  if (!item) return;
  for (const ref of [item.id, item.ref, asObject(item.api)?.id, asObject(item.emit)?.ref]) {
    if (typeof ref === 'string' && ref) output.add(ref);
  }
}

function asObject(value: unknown): JsonObject | undefined {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as JsonObject : undefined;
}

function groupBy<T>(
  entries: readonly T[],
  key: (entry: T) => string,
): ReadonlyMap<string, readonly T[]> {
  const grouped = new Map<string, T[]>();
  for (const entry of entries) {
    const selected = grouped.get(key(entry)) ?? [];
    selected.push(entry);
    grouped.set(key(entry), selected);
  }
  return grouped;
}

function normalizePath(path: string): string {
  return path.replaceAll('\\', '/').replace(/^\.\//, '').replace(/\/+/g, '/');
}
