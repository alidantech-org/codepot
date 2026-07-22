import type {
  ArrayUsageOptions,
  AuthoringRef,
  AuthoringRefBase,
  AuthoringRefKind,
  ExtendableAuthoringRef,
  ExtendableRefUsage,
  RefUsage,
  RefUsageOptions,
} from '@/contract/types/authoring/3.authoring-ref';

export interface CreateAuthoringRefInput<TTarget, TKind extends AuthoringRefKind> {
  readonly id: string;
  readonly kind: TKind;
  readonly key: string;
}

// ============================================================================
// INTERNAL
// ============================================================================

function createBaseRef<TTarget, TKind extends AuthoringRefKind>(
  input: CreateAuthoringRefInput<TTarget, TKind>,
): AuthoringRefBase<TTarget, TKind> {
  return {
    id: input.id,
    kind: input.kind,
    key: input.key,
  };
}

// ============================================================================
// AUTHORING REF FACTORIES
// ============================================================================

export function createAuthoringRef<TTarget, TKind extends AuthoringRefKind>(
  input: CreateAuthoringRefInput<TTarget, TKind>,
): AuthoringRef<TTarget, TKind> {
  const base = createBaseRef(input);

  return {
    ...base,

    optional() {
      return createUsage(base, { required: false });
    },

    required() {
      return createUsage(base, { required: true });
    },

    nullable() {
      return createUsage(base, { nullable: true });
    },

    nonNullable() {
      return createUsage(base, { nullable: false });
    },

    array(options: true | ArrayUsageOptions = true) {
      return createUsage(base, { array: options });
    },

    single() {
      return createUsage(base, { array: false });
    },
  };
}

export function createExtendableAuthoringRef<TTarget, TKind extends AuthoringRefKind, TExtension>(
  input: CreateAuthoringRefInput<TTarget, TKind>,
): ExtendableAuthoringRef<TTarget, TKind, TExtension> {
  const base = createBaseRef(input);

  return {
    ...base,

    optional() {
      return createExtendableUsage<TTarget, TKind, TExtension>(base, {
        required: false,
      });
    },

    required() {
      return createExtendableUsage<TTarget, TKind, TExtension>(base, {
        required: true,
      });
    },

    nullable() {
      return createExtendableUsage<TTarget, TKind, TExtension>(base, {
        nullable: true,
      });
    },

    nonNullable() {
      return createExtendableUsage<TTarget, TKind, TExtension>(base, {
        nullable: false,
      });
    },

    array(options: true | ArrayUsageOptions = true) {
      return createExtendableUsage<TTarget, TKind, TExtension>(base, {
        array: options,
      });
    },

    single() {
      return createExtendableUsage<TTarget, TKind, TExtension>(base, {
        array: false,
      });
    },

    extendWith(fields: TExtension) {
      return createExtendableUsage<TTarget, TKind, TExtension>(base, {
        extendWith: fields,
      });
    },
  };
}

// ============================================================================
// USAGE FACTORIES
// ============================================================================

export function createUsage<TTarget, TKind extends AuthoringRefKind>(
  ref: AuthoringRefBase<TTarget, TKind>,
  usage: RefUsageOptions<never> = {},
): RefUsage<TTarget, TKind> {
  return {
    ref: createAuthoringRef(ref),
    usage,

    optional() {
      return createUsage(ref, { ...usage, required: false });
    },

    required() {
      return createUsage(ref, { ...usage, required: true });
    },

    nullable() {
      return createUsage(ref, { ...usage, nullable: true });
    },

    nonNullable() {
      return createUsage(ref, { ...usage, nullable: false });
    },

    array(options: true | ArrayUsageOptions = true) {
      return createUsage(ref, { ...usage, array: options });
    },

    single() {
      return createUsage(ref, { ...usage, array: false });
    },
  };
}

export function createExtendableUsage<TTarget, TKind extends AuthoringRefKind, TExtension>(
  ref: AuthoringRefBase<TTarget, TKind>,
  usage: RefUsageOptions<TExtension> = {},
): ExtendableRefUsage<TTarget, TKind, TExtension> {
  return {
    ref: createExtendableAuthoringRef<TTarget, TKind, TExtension>(ref),
    usage,

    optional() {
      return createExtendableUsage(ref, { ...usage, required: false });
    },

    required() {
      return createExtendableUsage(ref, { ...usage, required: true });
    },

    nullable() {
      return createExtendableUsage(ref, { ...usage, nullable: true });
    },

    nonNullable() {
      return createExtendableUsage(ref, { ...usage, nullable: false });
    },

    array(options: true | ArrayUsageOptions = true) {
      return createExtendableUsage(ref, { ...usage, array: options });
    },

    single() {
      return createExtendableUsage(ref, { ...usage, array: false });
    },

    extendWith(fields: TExtension) {
      return createExtendableUsage(ref, {
        ...usage,
        extendWith: fields,
      });
    },
  };
}
