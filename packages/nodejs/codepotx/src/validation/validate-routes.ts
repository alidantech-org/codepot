import type { RouteRegistry } from '../routes/route.types.js';
import { validateRouteSchema } from './validate-route-schema.js';
import type { ValidationIssue } from './validation-result.types.js';

export function validateRoutes(registry: RouteRegistry): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  if (registry.params) {
    issues.push(...validateRouteSchema(registry.params, 'params'));
  }

  for (const [key, route] of Object.entries(registry.routes)) {
    const basePath = `routes.${key}`;

    issues.push(...validateRouteSchema(route.query, `${basePath}.query`));
    issues.push(...validateRouteSchema(route.body, `${basePath}.body`));
    issues.push(...validateRouteSchema(route.response, `${basePath}.response`));

    for (const [status, response] of Object.entries(route.responses ?? {})) {
      issues.push(...validateRouteSchema(response, `${basePath}.responses.${status}`));
    }
  }

  return issues;
}
