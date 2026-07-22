import type { VersionContract } from '../version/version-contract.types.js';
import type { ValidationIssue } from './validation-result.types.js';

export function validateDuplicates(contract: VersionContract): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  issues.push(
    ...findDuplicates(
      contract.resources.map((resource) => resource.context.name),
      'resources',
    ),
  );

  issues.push(
    ...findRegistryDuplicates(
      contract.properties.map((registry) => registry.name),
      'properties',
    ),
  );

  issues.push(
    ...findRegistryDuplicates(
      contract.schemaComponents.map((registry) => registry.name),
      'schemaComponents',
    ),
  );

  issues.push(
    ...findRegistryDuplicates(
      contract.parameterComponents.map((registry) => registry.name),
      'parameterComponents',
    ),
  );

  issues.push(
    ...findRegistryDuplicates(
      contract.requestBodyComponents.map((registry) => registry.name),
      'requestBodyComponents',
    ),
  );

  issues.push(
    ...findRegistryDuplicates(
      contract.responseComponents.map((registry) => registry.name),
      'responseComponents',
    ),
  );

  for (const resource of contract.resources) {
    const basePath = `resources.${resource.context.name}`;

    issues.push(
      ...findRegistryDuplicates(
        resource.properties.map((registry) => registry.name),
        `${basePath}.properties`,
      ),
    );

    // For schema components, check individual definition names, not registry names
    const schemaDefinitionNames = resource.schemaComponents.flatMap((registry) => registry.definitions.map((def) => def.name));
    issues.push(...findRegistryDuplicates(schemaDefinitionNames, `${basePath}.schemaComponents`));

    issues.push(
      ...findRegistryDuplicates(
        resource.parameterComponents.map((registry) => registry.name),
        `${basePath}.parameterComponents`,
      ),
    );

    issues.push(
      ...findRegistryDuplicates(
        resource.requestBodyComponents.map((registry) => registry.name),
        `${basePath}.requestBodyComponents`,
      ),
    );

    issues.push(
      ...findRegistryDuplicates(
        resource.responseComponents.map((registry) => registry.name),
        `${basePath}.responseComponents`,
      ),
    );

    issues.push(
      ...findRegistryDuplicates(
        resource.routeRegistries.map((registry) => registry.name),
        `${basePath}.routes`,
      ),
    );
  }

  return issues;
}

function findRegistryDuplicates(names: string[], path: string): ValidationIssue[] {
  return findDuplicates(names, path);
}

function findDuplicates(names: string[], path: string): ValidationIssue[] {
  const seen = new Set<string>();
  const issues: ValidationIssue[] = [];

  for (const name of names) {
    if (!seen.has(name)) {
      seen.add(name);
      continue;
    }

    issues.push({
      path,
      message: `Duplicate name found: ${name}`,
    });
  }

  return issues;
}
