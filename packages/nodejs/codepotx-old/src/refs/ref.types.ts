import { RefKind } from './ref-kind.js';
import type { CodegenMetadata, XCodegenResourceMeta } from '../codegen/codegen-extension.types.js';
import type { RefUsage, RefWithUsageMethods } from './ref-usage.types.js';
import type { SchemaFieldMap } from '../schema/schema.types.js';
import type { AccessRef } from '../access/access.types.js';

export interface GeneratedEnumPropertySchema {
  readonly kind: 'enum';
  readonly values: readonly string[];
}

export interface GeneratedBooleanPropertySchema {
  readonly kind: 'boolean';
}

export type GeneratedPropertySchema = GeneratedEnumPropertySchema | GeneratedBooleanPropertySchema;

export interface EngineRefBase {
  readonly id: string;
  readonly name: string;
  readonly kind: RefKind;
  readonly meta?: CodegenMetadata;
}

export interface PropertyRef extends EngineRefBase {
  readonly kind: typeof RefKind.property;
  readonly propertyKey: string;
  readonly targetRefId?: string;
  readonly generatedSchema?: GeneratedPropertySchema;
}

export interface ComponentRef extends EngineRefBase {
  readonly kind: typeof RefKind.component;
  readonly componentKey: string;
}

export interface ParameterRef extends EngineRefBase {
  readonly kind: typeof RefKind.parameter;
  readonly parameterKey: string;
}

export interface RequestBodyRef extends EngineRefBase {
  readonly kind: typeof RefKind.requestBody;
  readonly requestBodyKey: string;
}

export interface ResponseRef extends EngineRefBase {
  readonly kind: typeof RefKind.response;
  readonly responseKey: string;
}

export interface ModelRef extends EngineRefBase {
  readonly kind: typeof RefKind.model;
  readonly modelKey: string;
  readonly fields: Record<string, RefWithUsageMethods<PropertyRef> | RefUsage<PropertyRef>>;
  readonly sourceFields?: SchemaFieldMap;
  readonly openapiRef?: string;
  readonly inherits?: readonly {
    readonly modelRef: ModelRef;
    readonly fields: readonly string[];
  }[];
  readonly abstract?: boolean;
}

export interface RouteRef extends EngineRefBase {
  readonly kind: typeof RefKind.route;
  readonly routeKey: string;
  readonly method: string;
  readonly path: string;
  readonly resource?: XCodegenResourceMeta;
  readonly query?: unknown;
  readonly body?: unknown;
  readonly response?: unknown;
  readonly access?: AccessRef;
  readonly runtime?: import('../hooks/runtime-hooks.types.js').RuntimeRouteConfig;
  readonly sources: Record<string, import('../routes/route.types.js').RouteSourceRef>;
  readonly defaultSource?: import('../routes/route.types.js').RouteSourceRef;
}

export interface OperationRef extends EngineRefBase {
  readonly kind: typeof RefKind.operation;
  readonly operationId: string;
}

export type EngineRef = PropertyRef | ComponentRef | ModelRef | ParameterRef | RequestBodyRef | ResponseRef | RouteRef | OperationRef;
