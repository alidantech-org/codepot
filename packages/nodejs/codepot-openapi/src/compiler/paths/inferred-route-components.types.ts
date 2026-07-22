import type { ContentTypeInput } from '../../openapi/content-type.js';
import type { ComponentRef, ModelRef } from '../../refs/ref.types.js';
import type { FieldSourceMetadata, RefUsage } from '../../refs/ref-usage.types.js';
import type { RouteBodyInput, RouteParameterFieldValue, RouteResponseInput, RouteSchemaInput } from '../../routes/route.types.js';

export type InferredQueryParameterSchema = RouteParameterFieldValue | ModelRef | ComponentRef | RefUsage<ModelRef> | RefUsage<ComponentRef>;

export interface InferredParameterComponent {
  readonly name: string;
  readonly parameterName: string;
  readonly in: 'path' | 'query';
  readonly required: boolean;
  readonly schema: InferredQueryParameterSchema;
  readonly resourceKey?: string;
  readonly operationId?: string;
  readonly source?: FieldSourceMetadata;
}

export interface InferredRequestBodyComponent {
  readonly name: string;
  readonly required: boolean;
  readonly schema: RouteBodyInput | RouteSchemaInput;
  readonly description?: string;
  readonly contentType: ContentTypeInput;
  readonly resourceKey?: string;
  readonly operationId: string;
}

export interface InferredResponseComponent {
  readonly name: string;
  readonly status: number;
  readonly schema?: RouteResponseInput | RouteSchemaInput;
  readonly description: string;
  readonly contentType?: ContentTypeInput;
  readonly resourceKey?: string;
  readonly operationId: string;
  readonly noContent?: boolean;
}

export interface InferredRouteComponents {
  readonly parameters: Map<string, InferredParameterComponent>;
  readonly requestBodies: Map<string, InferredRequestBodyComponent>;
  readonly responses: Map<string, InferredResponseComponent>;
}
