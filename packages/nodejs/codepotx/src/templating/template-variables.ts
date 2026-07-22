import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from '@/contract/index';
import type {
  CompiledTemplatePack,
  DataCodecPort,
  Diagnostic,
  HashPort,
  JsonObject,
  JsonValue,
  TemplateContextValidation,
  TemplateHelperDescriptor,
  TemplatePartialDescriptor,
  TemplateVariableCatalog,
  TemplateVariableEntry,
  TemplateVariableKind,
  TemplateVariableOrigin,
  TemplateVariableRequirement,
  TemplateVariableScope,
} from '@/contract/index';

import { BUILTIN_TEMPLATE_HELPERS } from './helpers';
import { validatePathExpression, validateTemplateReferences } from './template-references';

export interface TemplateCatalogDependencies {
  readonly hashes: HashPort;
  readonly data: DataCodecPort;
}

/** Build a flattened deterministic catalog from the exact render context. */
export async function buildTemplateVariableCatalog(
  context: JsonObject,
  templates: CompiledTemplatePack,
  dependencies: TemplateCatalogDependencies,
): Promise<TemplateVariableCatalog> {
  const baseEntries = collectVariableEntries(context);
  const entries = expandFolderAliases(baseEntries, templates);
  const partials = collectPartials(templates);
  const helpers = mergeHelpers(templates.manifest.helpers);
  const requirements = templates.manifest.variableRequirements;
  const diagnostics = validateRequirements(requirements, entries);
  const dataVariables = handlebarsDataVariables();
  const roots = [...new Set([
    ...Object.keys(context),
    ...templates.folders.flatMap((folder) => folder.alias ?? folder.name),
    ...(templates.folders.some((folder) => folder.mode === 'group') ? ['items'] : []),
  ])].sort();
  const body = { roots, entries, helpers, partials, dataVariables, requirements, diagnostics } as const;
  const contentDigest = await dependencies.hashes.text(dependencies.data.stringifyJson(body));
  return {
    header: {
      kind: 'codepot.template-variables',
      protocolVersion: CODEPOT_PROTOCOL_VERSION,
      artifactVersion: CODEPOT_ARTIFACT_VERSION,
      producer: { name: 'codepotx', version: '0.0.0' },
      contentDigest,
      sourceDigest: await dependencies.hashes.values([
        templates.header.contentDigest,
        contentDigest,
      ]),
    },
    ...body,
  };
}

export function validateTemplateContext(
  catalog: TemplateVariableCatalog,
  templates: CompiledTemplatePack,
  strict = true,
): TemplateContextValidation {
  const references = templates.templates.flatMap((template) => template.references);
  const validated = validateTemplateReferences(references, catalog, strict);
  const pathDiagnostics = templates.templates.flatMap((template) => template.outputTokens
    .filter((token) => token.kind === 'dynamic' && token.expression)
    .map((token) => validatePathExpression(token.expression!, catalog))
    .filter((item): item is Diagnostic => Boolean(item)));
  const diagnostics = [...catalog.diagnostics, ...validated.diagnostics, ...pathDiagnostics];
  return {
    valid: diagnostics.every((item) => item.severity !== 'error'),
    catalog,
    references: validated.references,
    diagnostics,
  };
}

export function formatTemplateVariableCatalog(
  catalog: TemplateVariableCatalog,
  format: 'object' | 'json' | 'markdown',
  pretty = true,
): TemplateVariableCatalog | string {
  if (format === 'object') return catalog;
  if (format === 'json') return JSON.stringify(catalog, null, pretty ? 2 : 0);
  return [
    '# Codepot template variables',
    '',
    `Catalog digest: \`${catalog.header.contentDigest}\``,
    '',
    '## Variables',
    '',
    '| Path | Kind | Required | Nullable | Scope | Description |',
    '|---|---|---:|---:|---|---|',
    ...catalog.entries.map((entry) => `| \`${escapeTable(entry.path)}\` | ${entry.kind} | ${entry.required ? 'yes' : 'no'} | ${entry.nullable ? 'yes' : 'no'} | ${entry.scope} | ${escapeTable(entry.description ?? '')} |`),
    '',
    '## Helpers',
    '',
    '| Helper | Returns | Description |',
    '|---|---|---|',
    ...catalog.helpers.map((helper) => `| \`${helper.name}\` | ${helper.returns} | ${escapeTable(helper.description)} |`),
    '',
    '## Partials',
    '',
    ...(catalog.partials.length
      ? catalog.partials.map((partial) => `- \`{{> ${partial.name}}}\` — \`${partial.path}\``)
      : ['No partials are registered.']),
    '',
    '## Handlebars data variables',
    '',
    ...catalog.dataVariables.map((entry) => `- \`${entry.path}\` — ${entry.description ?? entry.kind}`),
    '',
  ].join('\n');
}

export function collectVariableEntries(context: JsonObject): readonly TemplateVariableEntry[] {
  const entries = new Map<string, TemplateVariableEntry>();
  const visit = (path: string, value: JsonValue, required: boolean): void => {
    mergeEntry(entries, variableEntry(path, value, required));
    if (Array.isArray(value)) {
      for (const item of value) visit(`${path}[]`, item, true);
      return;
    }
    if (!value || typeof value !== 'object') return;
    const object = value as JsonObject;
    for (const key of Object.keys(object).sort()) visit(`${path}.${key}`, object[key]!, true);
  };
  for (const root of Object.keys(context).sort()) visit(root, context[root]!, true);
  return [...entries.values()].sort((left, right) => left.path.localeCompare(right.path));
}

/**
 * A folder selector such as `schemas.models` exposes one selected item as
 * `model`. Clone the selected variable subtree so validation and documentation
 * describe the exact per-file alias that template authors use.
 */
function expandFolderAliases(
  baseEntries: readonly TemplateVariableEntry[],
  templates: CompiledTemplatePack,
): readonly TemplateVariableEntry[] {
  const output = new Map(baseEntries.map((entry) => [entry.path, entry]));
  for (const folder of templates.folders) {
    if (!folder.select || folder.mode === 'once') continue;
    const alias = folder.alias ?? folder.name;
    const selectedRoot = folder.mode === 'each' ? `${folder.select}[]` : folder.select;
    const matches = baseEntries.filter((entry) =>
      entry.path === selectedRoot || entry.path.startsWith(`${selectedRoot}.`));
    for (const entry of matches) {
      const suffix = entry.path.slice(selectedRoot.length);
      mergeEntry(output, {
        ...entry,
        path: `${alias}${suffix}`,
        name: suffix ? entry.name : alias,
        required: true,
        origins: uniqueOrigins([
          ...entry.origins,
          {
            layer: 'derived',
            path: folder.select,
            description: `Per-file alias declared by template folder ${folder.name}.`,
          },
        ]),
      });
      if (folder.mode === 'group') {
        mergeEntry(output, {
          ...entry,
          path: `items${suffix}`,
          name: suffix ? entry.name : 'items',
          required: true,
          origins: uniqueOrigins([
            ...entry.origins,
            {
              layer: 'derived',
              path: folder.select,
              description: `Grouped items declared by template folder ${folder.name}.`,
            },
          ]),
        });
      }
    }
    if (!matches.length) {
      mergeEntry(output, {
        path: alias,
        name: alias,
        kind: folder.mode === 'group' ? 'array' : 'unknown',
        scope: scopeForAlias(alias),
        required: true,
        nullable: false,
        origins: [{
          layer: 'derived',
          path: folder.select,
          description: `Alias declared by template folder ${folder.name}; selector has no current sample values.`,
        }],
      });
    }
  }
  return [...output.values()].sort((left, right) => left.path.localeCompare(right.path));
}

function variableEntry(path: string, value: JsonValue, required: boolean): TemplateVariableEntry {
  const description = descriptionForPath(path);
  return {
    path,
    name: path.split('.').at(-1)?.replace(/\[\]$/, '') ?? path,
    kind: valueKind(value),
    scope: scopeForPath(path),
    required,
    nullable: value === null,
    ...(Array.isArray(value) ? { itemKind: commonArrayKind(value) } : {}),
    ...(description ? { description } : {}),
    origins: [originForPath(path)],
  };
}

function mergeEntry(target: Map<string, TemplateVariableEntry>, incoming: TemplateVariableEntry): void {
  const current = target.get(incoming.path);
  if (!current) {
    target.set(incoming.path, incoming);
    return;
  }
  target.set(incoming.path, {
    ...current,
    kind: current.kind === incoming.kind ? current.kind : 'unknown',
    nullable: current.nullable || incoming.nullable,
    required: current.required && incoming.required,
    ...(current.itemKind === incoming.itemKind && current.itemKind ? { itemKind: current.itemKind } : {}),
    origins: uniqueOrigins([...current.origins, ...incoming.origins]),
  });
}

function collectPartials(templates: CompiledTemplatePack): readonly TemplatePartialDescriptor[] {
  return templates.templates
    .filter((template) => template.kind === 'partial' && template.partialName)
    .map((template) => ({ name: template.partialName!, templateId: template.id, path: template.path }))
    .sort((left, right) => left.name.localeCompare(right.name));
}

function mergeHelpers(requested: readonly string[]): readonly TemplateHelperDescriptor[] {
  const known = new Map(BUILTIN_TEMPLATE_HELPERS.map((helper) => [helper.name, helper]));
  for (const name of requested) {
    if (!known.has(name)) known.set(name, {
      name,
      description: 'Template-pack helper not provided by the default runtime.',
      arguments: [],
      returns: 'unknown',
      block: false,
    });
  }
  return [...known.values()].sort((left, right) => left.name.localeCompare(right.name));
}

function validateRequirements(
  requirements: readonly TemplateVariableRequirement[],
  entries: readonly TemplateVariableEntry[],
): Diagnostic[] {
  const byPath = new Map(entries.map((entry) => [entry.path, entry]));
  const diagnostics: Diagnostic[] = [];
  for (const requirement of requirements) {
    const entry = byPath.get(requirement.path);
    if (!entry && requirement.required) diagnostics.push({
      code: 'TEMPLATING_REQUIRED_VARIABLE_MISSING',
      severity: 'error',
      layer: 'templating',
      message: `Required template variable is unavailable: ${requirement.path}`,
      details: { path: requirement.path },
    });
    if (entry && requirement.kind && entry.kind !== requirement.kind && entry.kind !== 'unknown') diagnostics.push({
      code: 'TEMPLATING_VARIABLE_KIND_MISMATCH',
      severity: 'error',
      layer: 'templating',
      message: `Template variable ${requirement.path} is ${entry.kind}; expected ${requirement.kind}.`,
      details: { path: requirement.path, actual: entry.kind, expected: requirement.kind },
    });
  }
  return diagnostics;
}

function handlebarsDataVariables(): readonly TemplateVariableEntry[] {
  const values: readonly [string, TemplateVariableKind, string][] = [
    ['@root', 'object', 'Root template context.'],
    ['@index', 'number', 'Current array index inside each.'],
    ['@key', 'string', 'Current object key inside each.'],
    ['@first', 'boolean', 'True for the first item inside each.'],
    ['@last', 'boolean', 'True for the last item inside each.'],
  ];
  return values.map(([path, kind, description]) => ({
    path,
    name: path.slice(1),
    kind,
    scope: 'runtime',
    required: false,
    nullable: false,
    description,
    origins: [{ layer: 'runtime', description: 'Handlebars data variable.' }],
  }));
}

function valueKind(value: JsonValue): TemplateVariableKind {
  if (value === null) return 'null';
  if (Array.isArray(value)) return 'array';
  if (typeof value === 'string') return 'string';
  if (typeof value === 'number') return 'number';
  if (typeof value === 'boolean') return 'boolean';
  if (typeof value === 'object') return 'object';
  return 'unknown';
}

function commonArrayKind(values: readonly JsonValue[]): TemplateVariableKind {
  if (!values.length) return 'unknown';
  const kinds = new Set(values.map(valueKind));
  return kinds.size === 1 ? [...kinds][0]! : 'unknown';
}

function scopeForAlias(alias: string): TemplateVariableScope {
  if (alias.includes('model') || alias === 'dto' || alias.includes('schema') || alias.includes('enum')) return 'schema';
  if (alias.includes('operation') || alias.includes('route')) return 'operation';
  if (alias.includes('resource') || alias.includes('feature')) return 'resource';
  if (alias.includes('entity')) return 'entity';
  if (alias.includes('frontend') || alias.includes('screen')) return 'frontend';
  return 'root';
}

function scopeForPath(path: string): TemplateVariableScope {
  if (path.startsWith('project')) return 'project';
  if (path.startsWith('authoring') || path.startsWith('api')) return 'authoring';
  if (path.startsWith('resources') || path.startsWith('features')) return 'resource';
  if (path.startsWith('schemas')) return path.includes('.fields[]') ? 'field' : 'schema';
  if (path.startsWith('entities')) return path.includes('.fields[]') ? 'field' : 'entity';
  if (path.startsWith('operations')) {
    if (path.includes('.parameters[]')) return 'parameter';
    if (path.includes('.requestBody') || path.includes('.request_body')) return 'requestBody';
    if (path.includes('.responses[]')) return 'response';
    return 'operation';
  }
  if (path.startsWith('frontends') || path.startsWith('frontend') || path.startsWith('selected')) return 'frontend';
  if (path.startsWith('variables')) return 'variables';
  if (path.startsWith('lang') || path.startsWith('language')) return 'language';
  if (path.startsWith('emit')) return 'emit';
  if (path.startsWith('file')) return 'file';
  return 'root';
}

function originForPath(path: string): TemplateVariableOrigin {
  const scope = scopeForPath(path);
  if (scope === 'project') return { layer: 'project', path };
  if (scope === 'variables') return { layer: 'task', path };
  if (scope === 'emit' || scope === 'file') return { layer: 'generation', path };
  if (scope === 'language') return { layer: 'templating', path };
  if (scope === 'root') return { layer: 'derived', path };
  return { layer: 'authoring', path };
}

function descriptionForPath(path: string): string | undefined {
  const descriptions: Readonly<Record<string, string>> = {
    project: 'Project/package metadata prepared for templates.',
    api: 'Compatibility alias for the stable authoring artifact.',
    authoring: 'Complete stable authoring artifact.',
    resources: 'Resource template views.',
    features: 'Compatibility alias for resources.',
    schemas: 'Classified schema groups and views.',
    operations: 'Operation template views.',
    entities: 'Entity template views.',
    frontends: 'Frontend template views.',
    variables: 'Consumer task variables from CodepotFile.yml.',
    language: 'Injected target language metadata.',
    lang: 'Compatibility alias for language.',
    emit: 'Generation and output metadata.',
    file: 'Current output-file metadata.',
    meta: 'Derived counts and context metadata.',
  };
  return descriptions[path];
}

function uniqueOrigins(origins: readonly TemplateVariableOrigin[]): readonly TemplateVariableOrigin[] {
  const seen = new Set<string>();
  return origins.filter((origin) => {
    const key = `${origin.layer}:${origin.path ?? ''}:${origin.ref ?? ''}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function escapeTable(value: string): string {
  return value.replaceAll('|', '\\|').replaceAll('\n', ' ');
}
