import type { CompiledPathToken } from '@/contract/index';

export function resolveOutputTokens(
  tokens: readonly CompiledPathToken[],
  context: Record<string, unknown>,
): string {
  return tokens
    .map((token) => resolveToken(token, context))
    .filter(Boolean)
    .join('/');
}

export function resolveExpression(
  context: Record<string, unknown>,
  expression: string,
): unknown {
  return expression.split('.').filter(Boolean).reduce<unknown>((current, key) => {
    if (!current || typeof current !== 'object') return undefined;
    return (current as Record<string, unknown>)[key];
  }, context);
}

function resolveToken(
  token: CompiledPathToken,
  context: Record<string, unknown>,
): string {
  if (token.kind === 'escapedFolder' || token.kind === 'escapedDynamic') {
    return token.raw;
  }
  if (token.kind === 'static') {
    return interpolateExpressions(token.raw, context);
  }

  return pathValue(
    resolveRequiredExpression(context, token.expression ?? ''),
    token.expression ?? '',
  );
}

function interpolateExpressions(
  raw: string,
  context: Record<string, unknown>,
): string {
  return raw.replace(/\[([^\[\]]+)\]/g, (_match, expression: string) =>
    pathValue(resolveRequiredExpression(context, expression.trim()), expression.trim()),
  );
}

function resolveRequiredExpression(
  context: Record<string, unknown>,
  expression: string,
): unknown {
  const value = resolveExpression(context, expression);
  if (value === undefined || value === null || value === '') {
    throw new Error(`Template path expression "${expression}" resolved to an empty value.`);
  }
  return value;
}

function pathValue(value: unknown, expression: string): string {
  if (Array.isArray(value)) {
    const joined = value.map((item) => pathValue(item, expression)).filter(Boolean).join('/');
    if (!joined) {
      throw new Error(`Template path expression "${expression}" resolved to an empty value.`);
    }
    return joined;
  }
  if (value && typeof value === 'object') {
    const object = value as Record<string, unknown>;
    for (const key of ['original', 'raw', 'path']) {
      const candidate = object[key];
      if (typeof candidate === 'string' && candidate) return candidate;
    }
    throw new Error(
      `Template path expression "${expression}" resolved to an object without a string name value.`,
    );
  }
  return String(value);
}
