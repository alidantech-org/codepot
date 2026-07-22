export function fixOpenApiSchema(schema: unknown): unknown {
  if (!isPlainObject(schema)) return schema;

  const obj = schema as Record<string, unknown>;

  fixIntegerBounds(obj);
  fixTupleArray(obj);
  fixNestedValues(obj);

  return obj;
}

function fixIntegerBounds(obj: Record<string, unknown>): void {
  if (obj.type === 'integer' && obj.exclusiveMinimum === 0) {
    delete obj.exclusiveMinimum;
    obj.minimum = 1;
  }

  if (obj.type === 'integer' && obj.exclusiveMaximum === 0) {
    delete obj.exclusiveMaximum;
    obj.maximum = -1;
  }
}

function fixTupleArray(obj: Record<string, unknown>): void {
  if (obj.type === 'array' && Array.isArray(obj.items)) {
    obj.prefixItems = obj.items;
    delete obj.items;
  }
}

function fixNestedValues(obj: Record<string, unknown>): void {
  for (const key of Object.keys(obj)) {
    const value = obj[key];

    if (Array.isArray(value)) {
      obj[key] = value.map(fixOpenApiSchema);
      continue;
    }

    if (isPlainObject(value)) {
      obj[key] = fixOpenApiSchema(value);
    }
  }
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}
