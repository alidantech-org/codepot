import {
  AuthoringRefKind,
  type CompositeAuthoringRef,
  type DtoAuthoringRef,
  type EntityAuthoringRef,
  type EntityFieldAuthoringRef,
  type EntityFieldSetAuthoringRef,
  type EnumAuthoringRef,
  type ErrorAuthoringRef,
  type ModelAuthoringRef,
  type OperationAuthoringRef,
  type ParamsAuthoringRef,
  type PrimitiveAuthoringRef,
  type PropertyAuthoringRef,
  type ResourceAuthoringRef,
  type RouteAuthoringRef,
  type SecurityCredentialAuthoringRef,
  type SecurityPolicyAuthoringRef,
  type SecurityPrincipalAuthoringRef,
} from '@/contract/types/authoring/3.authoring-ref';

import {
  EntityFieldSetNameValues,
  type EntityFieldSetName,
  type EntityFieldSetRefs,
  EntityModelVariantValues,
  type EntityModelVariant,
  type EntityModelRefs,
  type PropertySourceInput,
} from '@/contract/types/authoring/4.properties-builder';

import { createEngineId, EngineIdPart } from '@/contract/engine/engine-id';

import { createAuthoringRef, createExtendableAuthoringRef } from './create-authoring-ref';

// ============================================================================
// PROPERTIES
// ============================================================================

export function primitiveRef(key: string): PrimitiveAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.property, EngineIdPart.primitive, key),
    kind: AuthoringRefKind.propertyPrimitive,
    key,
  });
}

export function enumRef(key: string): EnumAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.property, EngineIdPart.enum, key),
    kind: AuthoringRefKind.propertyEnum,
    key,
  });
}

export function compositeRef(key: string): CompositeAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.property, EngineIdPart.composite, key),
    kind: AuthoringRefKind.propertyComposite,
    key,
  });
}

export function propertyRefFromSource(key: string, source: PropertySourceInput): PropertyAuthoringRef {
  if (source.kind === 'primitive') return primitiveRef(key);
  if (source.kind === 'enum') return enumRef(key);
  if (source.kind === 'composite') return compositeRef(key);

  return source.ref;
}

// ============================================================================
// SCHEMAS
// ============================================================================

export function entityRef(name: string): EntityAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.schema, EngineIdPart.entity, name),
    kind: AuthoringRefKind.schemaEntity,
    key: name,
  });
}

export function entityFieldRef(entityName: string, fieldKey: string): EntityFieldAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.schema, EngineIdPart.entity, entityName, EngineIdPart.field, fieldKey),
    kind: AuthoringRefKind.schemaEntityField,
    key: fieldKey,
  });
}

export function modelRef(entityName: string, variant: EntityModelVariant): ModelAuthoringRef {
  const key = `${entityName}:${variant}`;

  return createExtendableAuthoringRef({
    id: createEngineId(EngineIdPart.schema, EngineIdPart.model, entityName, variant),
    kind: AuthoringRefKind.schemaModel,
    key,
  }) as ModelAuthoringRef;
}

export function modelRefs(entityName: string): EntityModelRefs {
  return Object.fromEntries(EntityModelVariantValues.map((variant) => [variant, modelRef(entityName, variant)])) as EntityModelRefs;
}

export function entityFieldSetRef(entityName: string, setName: EntityFieldSetName): EntityFieldSetAuthoringRef {
  const key = `${entityName}:${setName}`;

  return createAuthoringRef({
    id: createEngineId(EngineIdPart.schema, EngineIdPart.entity, entityName, EngineIdPart.fieldSet, setName),
    kind: AuthoringRefKind.schemaEntityFieldSet,
    key,
  });
}

export function entityFieldSetRefs(entityName: string): EntityFieldSetRefs {
  return Object.fromEntries(EntityFieldSetNameValues.map((name) => [name, entityFieldSetRef(entityName, name)])) as EntityFieldSetRefs;
}

export function dtoRef(key: string): DtoAuthoringRef {
  return createExtendableAuthoringRef({
    id: createEngineId(EngineIdPart.schema, EngineIdPart.dto, key),
    kind: AuthoringRefKind.schemaDto,
    key,
  }) as DtoAuthoringRef;
}

export function paramsRef(key: string): ParamsAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.schema, EngineIdPart.params, key),
    kind: AuthoringRefKind.schemaParams,
    key,
  });
}

// ============================================================================
// RESOURCES
// ============================================================================

export function resourceRef(key: string): ResourceAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.resource, key),
    kind: AuthoringRefKind.resource,
    key,
  });
}

export function operationRef(resourceKey: string, key: string): OperationAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.resource, resourceKey, EngineIdPart.operation, key),
    kind: AuthoringRefKind.resourceOperation,
    key,
  });
}

export function routeRef(resourceKey: string, key: string): RouteAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.resource, resourceKey, EngineIdPart.route, key),
    kind: AuthoringRefKind.resourceRoute,
    key,
  });
}

// ============================================================================
// ERRORS
// ============================================================================

export function errorRef(key: string): ErrorAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.error, key),
    kind: AuthoringRefKind.error,
    key,
  });
}

// ============================================================================
// SECURITY
// ============================================================================

export function securityCredentialRef(key: string): SecurityCredentialAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.security, EngineIdPart.credential, key),
    kind: AuthoringRefKind.securityCredential,
    key,
  });
}

export function securityPrincipalRef(key: string): SecurityPrincipalAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.security, EngineIdPart.principal, key),
    kind: AuthoringRefKind.securityPrincipal,
    key,
  });
}

export function securityPolicyRef(key: string): SecurityPolicyAuthoringRef {
  return createAuthoringRef({
    id: createEngineId(EngineIdPart.security, EngineIdPart.policy, key),
    kind: AuthoringRefKind.securityPolicy,
    key,
  });
}
