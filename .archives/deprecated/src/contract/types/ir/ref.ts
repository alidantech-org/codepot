// src/contract/types/ir/ref.ts

/**
 * JSON/YAML reference used by the compiled Codepot spec.
 *
 * Authoring refs use id/kind/key internally, but compiled output must use
 * portable JSON references so the spec can be serialized and consumed by
 * codegen without authoring-layer knowledge.
 */
export interface Ref<_TypeTarget = unknown> {
  $ref: string;
}

export type RefLike<TypeTarget = unknown> = Ref<TypeTarget>;
