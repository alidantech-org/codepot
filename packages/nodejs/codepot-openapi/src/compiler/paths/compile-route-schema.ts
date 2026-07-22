import type { ComponentFieldMap } from '../../components/component.types.js';
import { compileComponentSchema } from '../schemas/compile-component-schema.js';
import { compilePropertySchema } from '../schemas/compile-property-schema.js';
import { resolvePendingRefs } from '../refs/resolve-pending-refs.js';
import type { RefResolver } from '../refs/ref-resolver.types.js';
import type { RouteSchemaInput, RouteSchemaRef } from '../../routes/route.types.js';
import { isEngineRef } from '../../validation/ref-guards.js';
import { isRefUsage } from '../../validation/ref-usage-guards.js';
import type { SchemaField } from '../../schema/schema.types.js';

export function compileRouteSchema(schema: RouteSchemaInput | RouteSchemaRef, resolver: RefResolver): unknown {
  // Handle SchemaField types (only if it's a schema helper output, not a ref)
  if (isSchemaHelperField(schema)) {
    return resolvePendingRefs(compilePropertySchema(schema as SchemaField), resolver);
  }

  // Handle ref usages
  if (isRefUsage(schema)) {
    return resolvePendingRefs({ $ref: `#pending/${schema.ref.id}` }, resolver);
  }

  // Handle engine refs (PropertyRef, ComponentRef, ModelRef)
  if (isEngineRef(schema)) {
    return resolvePendingRefs({ $ref: `#pending/${schema.id}` }, resolver);
  }

  // Handle legacy ComponentFieldMap
  return resolvePendingRefs(
    compileComponentSchema({
      name: 'InlineRouteSchema',
      value: schema as ComponentFieldMap,
    }),
    resolver,
  );
}

function isSchemaHelperField(value: unknown): boolean {
  if (!value || typeof value !== 'object' || !('kind' in value)) return false;
  const kind = value.kind as string;
  // Schema helper fields have kinds like 'primitive', 'composite', 'ref', 'record', etc.
  // But NOT 'property', 'component', 'model', 'parameter', 'requestBody', 'response'
  return (
    kind !== 'property' && kind !== 'component' && kind !== 'model' && kind !== 'parameter' && kind !== 'requestBody' && kind !== 'response'
  );
}
