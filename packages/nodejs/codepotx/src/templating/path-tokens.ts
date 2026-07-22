import type { CompiledPathToken, JsonValue } from '@/contract/index';

export function compilePathTokens(path: string): readonly CompiledPathToken[] {
  const normalized = path.replaceAll('\\', '/');
  return normalized.split('/').filter(Boolean).flatMap((part) => tokenizePart(part));
}

export function compilePathParts(parts: readonly JsonValue[]): readonly CompiledPathToken[] {
  return parts.flatMap((part) => {
    if (Array.isArray(part)) {
      if (part.length !== 1 || typeof part[0] !== 'string') {
        throw new Error('Dynamic paths.yaml parts must contain exactly one string expression.');
      }
      return [{ kind: 'dynamic' as const, raw: `[${part[0]}]`, expression: part[0] }];
    }
    if (typeof part !== 'string') {
      throw new Error(`Template path part must be a string or one-item expression array, received ${typeof part}.`);
    }
    return compilePathTokens(part);
  });
}

function tokenizePart(part: string): readonly CompiledPathToken[] {
  if (part.startsWith('\\{') && part.endsWith('}')) return [{ kind: 'escapedFolder', raw: part.slice(1) }];
  if (part.startsWith('\\[') && part.endsWith(']')) return [{ kind: 'escapedDynamic', raw: part.slice(1) }];
  if (part.startsWith('{') && part.endsWith('}')) return [{ kind: 'folder', raw: part, expression: part.slice(1, -1).trim() }];
  if (part.startsWith('[') && part.endsWith(']')) return [{ kind: 'dynamic', raw: part, expression: part.slice(1, -1).trim() }];
  return [{ kind: 'static', raw: part }];
}

export function resolveOutputTokens(tokens: readonly CompiledPathToken[], context: Record<string, unknown>): string {
  return tokens.map((token) => {
    if (token.kind === 'static') return token.raw;
    if (token.kind === 'escapedFolder' || token.kind === 'escapedDynamic') return token.raw;
    const value = resolveExpression(context, token.expression ?? '');
    if (value === undefined || value === null || value === '') {
      throw new Error(`Template path expression "${token.expression}" resolved to an empty value.`);
    }
    return Array.isArray(value) ? value.map(String).filter(Boolean).join('/') : String(value);
  }).filter(Boolean).join('/');
}

export function resolveExpression(context: Record<string, unknown>, expression: string): unknown {
  return expression.split('.').filter(Boolean).reduce<unknown>((current, key) => {
    if (!current || typeof current !== 'object') return undefined;
    return (current as Record<string, unknown>)[key];
  }, context);
}
