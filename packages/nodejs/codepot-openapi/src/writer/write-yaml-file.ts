import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

function findFunctionPath(value: unknown, path = '$'): string | undefined {
  if (typeof value === 'function') return path;

  if (!value || typeof value !== 'object') return undefined;

  if (Array.isArray(value)) {
    for (let index = 0; index < value.length; index += 1) {
      const found = findFunctionPath(value[index], `${path}[${index}]`);
      if (found) return found;
    }

    return undefined;
  }

  for (const [key, child] of Object.entries(value)) {
    const found = findFunctionPath(child, `${path}.${key}`);
    if (found) return found;
  }

  return undefined;
}

function findPendingRefPath(value: unknown, path = '$'): string | undefined {
  if (!value || typeof value !== 'object') return undefined;

  if (Array.isArray(value)) {
    for (let index = 0; index < value.length; index += 1) {
      const found = findPendingRefPath(value[index], `${path}[${index}]`);
      if (found) return found;
    }
    return undefined;
  }

  const record = value as Record<string, unknown>;

  if (typeof record.$ref === 'string' && record.$ref.startsWith('#pending/')) {
    return `${path}.$ref`;
  }

  for (const [key, child] of Object.entries(record)) {
    const found = findPendingRefPath(child, `${path}.${key}`);
    if (found) return found;
  }

  return undefined;
}

export function writeYamlFile(filePath: string, data: unknown): void {
  ensureFolder(path.dirname(filePath));

  const functionPath = findFunctionPath(data);

  if (functionPath) {
    throw new Error(`OpenAPI document contains a function at ${functionPath}`);
  }

  const pendingPath = findPendingRefPath(data);

  if (pendingPath) {
    throw new Error(`OpenAPI document contains unresolved pending ref at ${pendingPath}`);
  }

  fs.writeFileSync(filePath, yaml.dump(data, { indent: 2, lineWidth: -1 }), 'utf-8');
}

function ensureFolder(folder: string): void {
  if (!fs.existsSync(folder)) {
    fs.mkdirSync(folder, { recursive: true });
  }
}
