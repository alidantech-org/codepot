import Handlebars from 'handlebars';

import type {
  Diagnostic,
  TemplateReference,
  TemplateReferenceValidation,
  TemplateVariableCatalog,
} from '@/contract/index';

interface AstNode {
  readonly type?: string;
  readonly original?: string;
  readonly data?: boolean;
  readonly path?: AstNode;
  readonly params?: readonly AstNode[];
  readonly hash?: { readonly pairs?: readonly { readonly value?: AstNode }[] };
  readonly program?: AstNode;
  readonly inverse?: AstNode;
  readonly body?: readonly AstNode[];
  readonly name?: string | AstNode;
  readonly blockParams?: readonly string[];
  readonly loc?: {
    readonly start?: { readonly line?: number; readonly column?: number };
    readonly end?: { readonly line?: number; readonly column?: number };
  };
  readonly [key: string]: unknown;
}

interface Scope {
  readonly currentPath: string | undefined;
  readonly aliases: ReadonlyMap<string, string>;
  readonly parents: readonly (string | undefined)[];
}

const ROOTS = new Set([
  'project', 'api', 'authoring', 'resources', 'features', 'schemas',
  'operations', 'entities', 'frontends', 'frontend', 'selectedFrontend',
  'selected_frontend', 'selectedFrontends', 'selected_frontends',
  'frontendCount', 'frontend_count', 'variables', 'language', 'lang',
  'emit', 'file', 'meta',
]);

const BLOCK_HELPERS = new Set(['each', 'if', 'unless', 'with', 'lookup', 'log']);

/** Parse Handlebars references without compiling or executing user templates. */
export function collectTemplateReferences(
  templateId: string,
  source: string,
  knownHelpers: ReadonlySet<string>,
): readonly TemplateReference[] {
  const ast = Handlebars.parse(source) as unknown as AstNode;
  const output: TemplateReference[] = [];
  const seen = new Set<string>();

  const add = (item: TemplateReference): void => {
    const location = item.location;
    const key = `${item.kind}:${item.name}:${item.resolvedPath ?? ''}:${location?.line ?? 0}:${location?.column ?? 0}`;
    if (seen.has(key)) return;
    seen.add(key);
    output.push(item);
  };

  const walkProgram = (program: AstNode | undefined, scope: Scope): void => {
    for (const node of program?.body ?? []) walk(node, scope);
  };

  const walk = (node: AstNode | undefined, scope: Scope): void => {
    if (!node) return;
    switch (node.type) {
      case 'Program':
        walkProgram(node, scope);
        return;
      case 'BlockStatement':
      case 'DecoratorBlock': {
        const helperName = original(node.path);
        if (helperName) add(makeReference(templateId, 'helper', helperName, undefined, node.path ?? node));
        collectArguments(node, scope, templateId, knownHelpers, add);
        const selected = firstPath(node.params, scope);
        const childPath = helperName === 'each' && selected
          ? `${selected}[]`
          : helperName === 'with'
            ? selected
            : scope.currentPath;
        const aliases = new Map(scope.aliases);
        for (const alias of node.program?.blockParams ?? []) {
          if (!childPath) continue;
          aliases.set(alias, childPath);
          add(makeReference(templateId, 'blockParameter', alias, childPath, node.program ?? node));
        }
        walkProgram(node.program, {
          currentPath: childPath,
          aliases,
          parents: [...scope.parents, scope.currentPath],
        });
        walkProgram(node.inverse, scope);
        return;
      }
      case 'MustacheStatement':
      case 'Decorator':
      case 'SubExpression': {
        const name = original(node.path);
        const helper = Boolean(name && (
          knownHelpers.has(name)
          || BLOCK_HELPERS.has(name)
          || (node.params?.length ?? 0) > 0
          || (node.hash?.pairs?.length ?? 0) > 0
        ));
        if (name) {
          if (helper) add(makeReference(templateId, 'helper', name, undefined, node.path ?? node));
          else addPath(node.path ?? node, scope, templateId, add);
        }
        collectArguments(node, scope, templateId, knownHelpers, add);
        return;
      }
      case 'PartialStatement':
      case 'PartialBlockStatement': {
        const name = typeof node.name === 'string' ? node.name : original(node.name as AstNode | undefined);
        if (name) add(makeReference(templateId, 'partial', name, undefined, node));
        collectArguments(node, scope, templateId, knownHelpers, add);
        walkProgram(node.program, scope);
        return;
      }
      case 'PathExpression':
        addPath(node, scope, templateId, add);
        return;
      default:
        for (const value of Object.values(node)) {
          if (Array.isArray(value)) {
            for (const item of value) if (isNode(item)) walk(item, scope);
          } else if (isNode(value)) {
            walk(value, scope);
          }
        }
    }
  };

  walk(ast, { currentPath: undefined, aliases: new Map(), parents: [] });
  return output.sort((left, right) => {
    const leftLine = left.location?.line ?? 0;
    const rightLine = right.location?.line ?? 0;
    return leftLine - rightLine || left.name.localeCompare(right.name);
  });
}

export function validateTemplateReferences(
  references: readonly TemplateReference[],
  catalog: TemplateVariableCatalog,
  strict = true,
): { readonly references: readonly TemplateReferenceValidation[]; readonly diagnostics: readonly Diagnostic[] } {
  const variables = new Set(catalog.entries.map((entry) => entry.path));
  const data = new Set(catalog.dataVariables.map((entry) => entry.path));
  const helpers = new Set([...catalog.helpers.map((helper) => helper.name), ...BLOCK_HELPERS]);
  const partials = new Set(catalog.partials.map((partial) => partial.name));
  const validated: TemplateReferenceValidation[] = [];
  const diagnostics: Diagnostic[] = [];

  for (const reference of references) {
    const path = normalizeCatalogPath(reference.resolvedPath ?? reference.name);
    const valid = reference.kind === 'helper'
      ? helpers.has(reference.name)
      : reference.kind === 'partial'
        ? partials.has(reference.name)
        : reference.kind === 'data'
          ? data.has(reference.name)
          : reference.kind === 'blockParameter'
            ? true
            : hasCatalogPath(variables, path);
    const reason = valid ? undefined : `Unknown template ${reference.kind}: ${reference.name}`;
    validated.push({
      reference,
      valid,
      ...(reference.resolvedPath ? { resolvedPath: reference.resolvedPath } : {}),
      ...(reason ? { reason } : {}),
    });
    if (!valid) {
      diagnostics.push({
        code: `TEMPLATING_UNKNOWN_${reference.kind.toUpperCase()}`,
        severity: strict ? 'error' : 'warning',
        layer: 'templating',
        message: `${reason} in ${reference.templateId}.`,
        details: { templateId: reference.templateId, name: reference.name, path },
      });
    }
  }
  return { references: validated, diagnostics };
}

export function validatePathExpression(
  expression: string,
  catalog: TemplateVariableCatalog,
): Diagnostic | undefined {
  const path = normalizeCatalogPath(expression);
  const entries = new Set(catalog.entries.map((entry) => entry.path));
  if (hasCatalogPath(entries, path)) return undefined;
  return {
    code: 'TEMPLATING_UNKNOWN_PATH_VARIABLE',
    severity: 'error',
    layer: 'templating',
    message: `Unknown variable in template output path: ${expression}`,
    details: { expression, normalizedPath: path },
  };
}

function collectArguments(
  node: AstNode,
  scope: Scope,
  templateId: string,
  helpers: ReadonlySet<string>,
  add: (item: TemplateReference) => void,
): void {
  for (const parameter of node.params ?? []) collectArgument(parameter, scope, templateId, helpers, add);
  for (const pair of node.hash?.pairs ?? []) collectArgument(pair.value, scope, templateId, helpers, add);
}

function collectArgument(
  node: AstNode | undefined,
  scope: Scope,
  templateId: string,
  helpers: ReadonlySet<string>,
  add: (item: TemplateReference) => void,
): void {
  if (!node) return;
  if (node.type === 'PathExpression') addPath(node, scope, templateId, add);
  if (node.type === 'SubExpression') {
    const name = original(node.path);
    if (name) add(makeReference(templateId, helpers.has(name) ? 'helper' : 'variable', name, helpers.has(name) ? undefined : resolvePath(name, scope), node));
    collectArguments(node, scope, templateId, helpers, add);
  }
}

function addPath(
  node: AstNode,
  scope: Scope,
  templateId: string,
  add: (item: TemplateReference) => void,
): void {
  const raw = original(node);
  if (!raw || raw === 'this' || raw === '.') return;
  if (node.data || raw.startsWith('@')) {
    add(makeReference(templateId, 'data', raw.startsWith('@') ? raw : `@${raw}`, undefined, node));
    return;
  }
  add(makeReference(templateId, 'variable', raw, resolvePath(raw, scope), node));
}

function resolvePath(raw: string, scope: Scope): string {
  const normalized = raw.replace(/^\.\//, '');
  const aliasRoot = normalized.split('.')[0]!;
  const alias = scope.aliases.get(aliasRoot);
  if (alias) return [alias, ...normalized.split('.').slice(1)].join('.');
  if (ROOTS.has(aliasRoot)) return normalized;
  if (normalized.startsWith('../')) {
    const levels = normalized.match(/^(?:\.\.\/)+/)?.[0].split('../').length! - 1;
    const parent = scope.parents[Math.max(0, scope.parents.length - levels)];
    return parent ? `${parent}.${normalized.replace(/^(?:\.\.\/)+/, '')}` : normalized.replace(/^(?:\.\.\/)+/, '');
  }
  return scope.currentPath ? `${scope.currentPath}.${normalized}` : normalized;
}

function firstPath(parameters: readonly AstNode[] | undefined, scope: Scope): string | undefined {
  const first = parameters?.[0];
  return first?.type === 'PathExpression' && original(first) ? resolvePath(original(first)!, scope) : undefined;
}

function makeReference(
  templateId: string,
  kind: TemplateReference['kind'],
  name: string,
  resolvedPath: string | undefined,
  node: AstNode,
): TemplateReference {
  const start = node.loc?.start;
  const end = node.loc?.end;
  return {
    templateId,
    kind,
    name,
    raw: name,
    ...(resolvedPath ? { resolvedPath } : {}),
    ...(start?.line !== undefined && start.column !== undefined ? {
      location: {
        line: start.line,
        column: start.column,
        ...(end?.line === undefined ? {} : { endLine: end.line }),
        ...(end?.column === undefined ? {} : { endColumn: end.column }),
      },
    } : {}),
  };
}

function original(node: AstNode | undefined): string | undefined {
  return typeof node?.original === 'string' ? node.original : undefined;
}

function normalizeCatalogPath(path: string): string {
  return path.replace(/^@root\./, '').replace(/\[\d+\]/g, '[]').replace(/\.\./g, '.');
}

function hasCatalogPath(entries: ReadonlySet<string>, path: string): boolean {
  if (entries.has(path)) return true;
  const parts = path.split('.');
  while (parts.length > 1) {
    parts.pop();
    if (entries.has(parts.join('.'))) return true;
  }
  return false;
}

function isNode(value: unknown): value is AstNode {
  return Boolean(value && typeof value === 'object' && typeof (value as AstNode).type === 'string');
}
