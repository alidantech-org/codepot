import type { VersionContract } from '../version/version-contract.types.js';
import { validateComponentFields, validateSchemaComponentValue } from './validate-component-fields.js';
import { validateDuplicates } from './validate-duplicates.js';
import { validateRoutes } from './validate-routes.js';
import type { ValidationIssue } from './validation-result.types.js';

export function validateVersionContract(contract: VersionContract): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  issues.push(...validateDuplicates(contract));

  for (const registry of contract.schemaComponents) {
    for (const component of registry.definitions) {
      issues.push(...validateSchemaComponentValue(component.value, `components.${component.name}`));
    }
  }

  for (const resource of contract.resources) {
    for (const registry of resource.schemaComponents) {
      for (const component of registry.definitions) {
        issues.push(...validateSchemaComponentValue(component.value, `resources.${resource.context.name}.components.${component.name}`));
      }
    }

    for (const routes of resource.routeRegistries) {
      issues.push(...validateRoutes(routes));
    }
  }

  return issues;
}
