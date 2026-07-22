import type { ComponentRef, ModelRef } from '../refs/ref.types.js';
import { toSchemaName } from './schema-name.js';

export function modelRefToSchemaName(ref: ModelRef): string {
  return toSchemaName(ref.name);
}

export function componentRefToSchemaName(ref: ComponentRef): string {
  return toSchemaName(ref.name);
}
