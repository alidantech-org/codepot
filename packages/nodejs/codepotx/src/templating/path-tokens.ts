import type { CompiledPathToken, JsonValue } from '@/contract/index';

export {
  resolveExpression,
  resolveOutputTokens,
} from '@/internal/paths/template-path-resolution';

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
  if (part.startsWith('\\{') && part.endsWith('}')) {
    return [{ kind: 'escapedFolder', raw: part.slice(1) }];
  }
  if (part.startsWith('\\[') && part.endsWith(']')) {
    return [{ kind: 'escapedDynamic', raw: part.slice(1) }];
  }
  if (part.startsWith('{') && part.endsWith('}')) {
    return [{ kind: 'folder', raw: part, expression: part.slice(1, -1).trim() }];
  }
  if (part.startsWith('[') && part.endsWith(']')) {
    return [{ kind: 'dynamic', raw: part, expression: part.slice(1, -1).trim() }];
  }
  return [{ kind: 'static', raw: part }];
}
