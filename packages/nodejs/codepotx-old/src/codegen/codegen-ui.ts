import { HttpMethod } from '../routes/http-method.js';
import type { CodegenUiInput, CodegenUiMeta, CodegenUiRole, ResolvedCodegenUiMeta } from './codegen-extension.types.js';

export function normalizeCodegenUiInput(input: CodegenUiInput | undefined): CodegenUiMeta | undefined {
  if (!input) return undefined;

  if (typeof input === 'string') {
    return {
      enabled: true,
      role: input,
    };
  }

  return {
    ...input,
    ...(input.role ? { enabled: input.enabled ?? true } : {}),
  };
}

export function resolveCodegenUi(input: {
  readonly operationUi?: CodegenUiMeta;
  readonly resourceUi?: CodegenUiMeta;
  readonly method: string;
  readonly fullPath: string;
  readonly resourcePath: string;
}): ResolvedCodegenUiMeta {
  if (input.operationUi?.enabled === false) {
    return { enabled: false };
  }

  if (input.resourceUi?.enabled === false) {
    return { enabled: false };
  }

  if (input.operationUi?.role) {
    return {
      enabled: true,
      role: input.operationUi.role,
      inferred: false,
    };
  }

  if (input.resourceUi?.enabled === true && input.resourceUi.infer === true) {
    const inferred = inferCodegenUiRole(input.method, input.fullPath, input.resourcePath);

    if (inferred) {
      return {
        enabled: true,
        role: inferred.role,
        inferred: true,
        inferenceSource: 'compiler',
        inferenceReason: inferred.reason,
      };
    }
  }

  return { enabled: false };
}

function inferCodegenUiRole(
  method: string,
  fullPath: string,
  resourcePath: string,
): { role: CodegenUiRole; reason: string } | undefined {
  if (fullPath === resourcePath) {
    if (method === HttpMethod.get) return { role: 'list', reason: 'GET collection route' };
    if (method === HttpMethod.post) return { role: 'create', reason: 'POST collection route' };
    return undefined;
  }

  if (isResourceItemPath(fullPath, resourcePath)) {
    if (method === HttpMethod.get) return { role: 'detail', reason: 'GET item route' };
    if (method === HttpMethod.patch) return { role: 'update', reason: 'PATCH item route' };
    if (method === HttpMethod.put) return { role: 'update', reason: 'PUT item route' };
    if (method === HttpMethod.delete) return { role: 'delete', reason: 'DELETE item route' };
  }

  return undefined;
}

function isResourceItemPath(fullPath: string, resourcePath: string): boolean {
  const suffix = fullPath.slice(resourcePath.length);
  return /^\/\{[A-Za-z_][A-Za-z0-9_]*\}$/.test(suffix);
}
