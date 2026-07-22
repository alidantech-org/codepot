export const XCodegenKind = {
  primitive: 'primitive',
  enum: 'enum',
  model: 'model',
  dto: 'dto',
} as const;

export type XCodegenKind = (typeof XCodegenKind)[keyof typeof XCodegenKind];

export const XCodegenEntityVariant = {
  partial: 'partial',
  full: 'full',
} as const;

export type XCodegenEntityVariant = (typeof XCodegenEntityVariant)[keyof typeof XCodegenEntityVariant];

export const XCodegenAccess = {
  default: 'default',
  public: 'public',
  internal: 'internal',
} as const;

export type XCodegenAccess = (typeof XCodegenAccess)[keyof typeof XCodegenAccess];

export const XCodegenDtoRole = {
  request: 'request',
  response: 'response',
  query: 'query',
  params: 'params',
  body: 'body',
  context: 'context',
} as const;

export type XCodegenDtoRole = (typeof XCodegenDtoRole)[keyof typeof XCodegenDtoRole];

export type CodegenUiRole = 'list' | 'detail' | 'create' | 'update' | 'delete' | 'action' | 'auth';

export interface CodegenUiMeta {
  readonly enabled?: boolean;
  readonly infer?: boolean;
  readonly role?: CodegenUiRole;
}

export interface ResolvedCodegenUiMeta {
  readonly enabled: boolean;
  readonly role?: CodegenUiRole;
  readonly inferred?: boolean;
  readonly inferenceSource?: 'compiler';
  readonly inferenceReason?: string;
}

export type CodegenUiInput = CodegenUiRole | CodegenUiMeta;

export interface CodegenCookieEffects {
  readonly set?: readonly string[];
  readonly clear?: readonly string[];
}

export interface CodegenOperationEffects {
  readonly cookies?: CodegenCookieEffects;
}

export interface XCodegenRefPointer {
  readonly $ref: string;
}

export interface XCodegenParameterTargetMeta {
  readonly $ref: string;
  readonly exclude?: readonly string[];
}

export interface XCodegenResourceMeta {
  /**
   * Resource output name.
   *
   * Example: "users", "vehicle_brands"
   */
  readonly name: string;

  /**
   * Output grouping folders.
   *
   * Example: ["platform", "auth"]
   */
  readonly path?: readonly string[];
}

export interface XCodegenEntityMeta {
  /**
   * Entity/model name.
   *
   * Example: "User", "Vehicle"
   */
  readonly name: string;

  /**
   * Entity shape.
   */
  readonly variant?: XCodegenEntityVariant;

  /**
   * Entity access level.
   */
  readonly access?: XCodegenAccess;
}

export interface XCodegenQueryMeta {
  /**
   * Whether this primitive model field can be used in filters.
   */
  readonly filter?: true;

  /**
   * Filter operators supported by this primitive model field.
   */
  readonly operators?: readonly string[];

  /**
   * Whether this primitive model field can be used in sort values.
   */
  readonly sort?: true;

  /**
   * Whether this primitive model field can be used in select values.
   */
  readonly select?: true;
}

export interface XCodegenBaseMeta {
  /**
   * Marks sensitive fields/components.
   */
  readonly sensitive?: true;

  /**
   * Marks reusable/shared generated components.
   */
  readonly shared?: true;

  /**
   * Marks abstract/base components.
   */
  readonly abstract?: true;

  /**
   * Marks components that should not be generated directly.
   */
  readonly skip?: true;

  /**
   * Stable internal reference id.
   */
  readonly refId?: string;

  /**
   * Resource ownership and output grouping.
   */
  readonly resource?: XCodegenResourceMeta;

  /**
   * Entity ownership and shape.
   */
  readonly entity?: XCodegenEntityMeta;

  /**
   * Parent schemas/components this component inherits from.
   */
  readonly inherits?: readonly XCodegenRefPointer[];

  /**
   * Optional pointer to the real generated target.
   *
   * Example:
   * Operation query params can point to the reusable UserListQuery schema.
   */
  readonly target?: XCodegenRefPointer;

  readonly projection?: {
    readonly source: string;
    readonly rootSource?: string;
    readonly mode: 'pick' | 'omit' | 'partial';
    readonly fields?: readonly string[];
    readonly steps?: readonly {
      readonly mode: 'pick' | 'omit' | 'partial';
      readonly fields?: readonly string[];
    }[];
  };

  readonly ui?: ResolvedCodegenUiMeta;

  readonly effects?: CodegenOperationEffects;
}

export interface XCodegenPrimitiveMeta extends XCodegenBaseMeta {
  readonly kind: typeof XCodegenKind.primitive;
  readonly role?: 'access-role';

  /**
   * Only valid on primitive fields inside model/entity definitions.
   */
  readonly query?: XCodegenQueryMeta;
}

export interface XCodegenEnumMeta extends XCodegenBaseMeta {
  readonly kind: typeof XCodegenKind.enum;
  readonly role?: 'access-role';
}

export interface XCodegenModelMeta extends XCodegenBaseMeta {
  readonly kind: typeof XCodegenKind.model;
}

export interface XCodegenDtoMeta extends XCodegenBaseMeta {
  readonly kind: typeof XCodegenKind.dto;

  /**
   * DTO role (single role).
   *
   * request  = generic request DTO
   * response = response DTO
   * query    = query string DTO
   * params   = path params DTO
   * body     = request body DTO
   *
   * Role is optional and should be determined by route usage.
   * Schemas defined via defineSchemas initially have no role.
   *
   * If a DTO is used in multiple roles, use `roles` instead.
   */
  readonly role?: XCodegenDtoRole;

  /**
   * DTO roles (multiple roles).
   *
   * Used when a DTO is reused in multiple contexts (e.g., both body and response).
   * If only one role applies, use `role` instead.
   */
  readonly roles?: readonly XCodegenDtoRole[];
}

export type CodegenMetadata = XCodegenPrimitiveMeta | XCodegenEnumMeta | XCodegenModelMeta | XCodegenDtoMeta;

export type CodegenKind = XCodegenKind;
