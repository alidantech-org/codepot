import type {
  JsonObject,
  TemplateVariableRequirement,
} from '@/contract/index';
import type {
  PathsFileInput,
  PathsFolderInput,
  TemplateVariableRequirementInput,
} from './paths-input.types';

export interface NormalizedWritePolicyInput {
  readonly defaultMode: 'managed' | 'immutable';
  readonly managedRoots: readonly string[];
  readonly immutableRoots: readonly string[];
  readonly protectedRoots: readonly string[];
  readonly cleanRoots: readonly string[];
}

export interface NormalizedPathsConfig {
  readonly name?: string;
  readonly version: string;
  readonly description?: string;
  readonly templateExtension: string;
  readonly stripTemplateExtension: boolean;
  readonly allowRawFiles: boolean;
  readonly includeHidden: boolean;
  readonly ignore: readonly string[];
  readonly helpers: readonly string[];
  readonly partials: readonly string[];
  readonly variableRequirements: readonly TemplateVariableRequirement[];
  readonly metadata?: JsonObject;
  readonly folders: Readonly<Record<string, PathsFolderInput>>;
  readonly write: NormalizedWritePolicyInput;
}

export function normalizePathsConfig(input: PathsFileInput): NormalizedPathsConfig {
  return {
    ...(input.name ? { name: input.name } : {}),
    version: input.version ?? '1.0.0',
    ...(input.description ? { description: input.description } : {}),
    templateExtension: input.templateExtension ?? input.template_extension ?? '.hbs',
    stripTemplateExtension:
      input.stripTemplateExtension ?? input.strip_template_extension ?? true,
    allowRawFiles: input.allowRawFiles ?? input.allow_raw_files ?? true,
    includeHidden: input.includeHidden ?? input.include_hidden ?? true,
    ignore: [...new Set(['paths.yaml', ...(input.ignore ?? [])])],
    helpers: input.helpers ?? [],
    partials: input.partials ?? [],
    variableRequirements: normalizeVariableRequirements(input.variables),
    ...(input.metadata ? { metadata: input.metadata } : {}),
    folders: input.folders ?? {},
    write: {
      defaultMode: input.write?.defaultMode
        ?? input.write?.default_mode
        ?? 'managed',
      managedRoots: input.write?.managedRoots
        ?? input.write?.managed_roots
        ?? [],
      immutableRoots: input.write?.immutableRoots
        ?? input.write?.immutable_roots
        ?? [],
      protectedRoots: input.write?.protectedRoots
        ?? input.write?.protected_roots
        ?? [],
      cleanRoots: input.write?.cleanRoots
        ?? input.write?.clean_roots
        ?? [],
    },
  };
}

function normalizeVariableRequirements(
  input: PathsFileInput['variables'],
): readonly TemplateVariableRequirement[] {
  if (!input) return [];
  if (Array.isArray(input)) {
    const entries = input as readonly TemplateVariableRequirementInput[];
    return entries.map((item) => normalizeRequirement(item, item.required ?? true))
      .sort((left, right) => left.path.localeCompare(right.path));
  }
  const grouped = input as {
    readonly required?: readonly (string | TemplateVariableRequirementInput)[];
    readonly optional?: readonly (string | TemplateVariableRequirementInput)[];
  };
  return [
    ...(grouped.required ?? []).map((item) => normalizeRequirement(item, true)),
    ...(grouped.optional ?? []).map((item) => normalizeRequirement(item, false)),
  ].sort((left, right) => left.path.localeCompare(right.path));
}

function normalizeRequirement(
  input: string | TemplateVariableRequirementInput,
  required: boolean,
): TemplateVariableRequirement {
  if (typeof input === 'string') return { path: input, required };
  return {
    path: input.path,
    required: input.required ?? required,
    ...(input.kind ? { kind: input.kind } : {}),
    ...(input.description ? { description: input.description } : {}),
  };
}
