import type { OpenApiVersion } from "../openapi/openapi-version.js";
import type { OpenApiServer } from "../openapi/openapi.types.js";

export interface CompileOptions {
  readonly openapi?: OpenApiVersion;
  readonly validate?: boolean;
  readonly servers?: readonly OpenApiServer[];
}
