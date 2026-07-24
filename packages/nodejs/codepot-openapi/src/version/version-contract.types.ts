import type { SchemaComponentRegistry } from '../components/schemas/schema-component.types.js';
import type { ParameterComponentRegistry } from '../components/parameters/parameter-component.types.js';
import type { RequestBodyComponentRegistry } from '../components/request-bodies/request-body-component.types.js';
import type { ResponseComponentRegistry } from '../components/responses/response-component.types.js';
import type { PropertyRegistry } from '../properties/property.types.js';
import type { ResourceBuilder } from '../resource/define-resource.js';
import type { RouteResponseInput } from '../routes/route.types.js';
import type { ContentTypeInput } from '../openapi/content-type.js';
import type { AccessRegistry } from '../access/access.types.js';
import type { EntityRegistry } from '../entities/entity.types.js';
import type { FrontendBuilder } from '../frontend/frontend.types.js';

export interface VersionLicense {
  readonly name: string;
  readonly identifier?: string;
  readonly url?: string;
}

export interface VersionInfo {
  title: string;
  version: string;
  description?: string;
  license?: VersionLicense;
}

export interface VersionDefaults {
  readonly requestContentType?: ContentTypeInput;
  readonly responseContentType?: ContentTypeInput;
}

export interface VersionContract {
  readonly info: VersionInfo;
  readonly tags: readonly string[];
  readonly defaults: VersionDefaults;
  readonly resources: ResourceBuilder[];
  readonly properties: PropertyRegistry[];
  readonly schemaComponents: SchemaComponentRegistry[];
  readonly parameterComponents: ParameterComponentRegistry[];
  readonly requestBodyComponents: RequestBodyComponentRegistry[];
  readonly responseComponents: ResponseComponentRegistry[];
  readonly accessComponents: AccessRegistry[];
  readonly baseEntityComponents: EntityRegistry[];
  readonly entityComponents: EntityRegistry[];
  readonly frontends: FrontendBuilder[];
  readonly defaultResponses: Record<number, RouteResponseInput>;
}
