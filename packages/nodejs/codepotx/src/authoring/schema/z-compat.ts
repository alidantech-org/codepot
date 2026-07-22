import { z as internalZod } from 'zod/v4';
import type * as z4 from 'zod/v4/core';

export interface CodepotZodCompatibility {
  readonly string: typeof internalZod.string;
  readonly number: typeof internalZod.number;
  readonly boolean: typeof internalZod.boolean;
  readonly bigint: typeof internalZod.bigint;
  readonly date: typeof internalZod.date;
  readonly literal: typeof internalZod.literal;
  readonly enum: typeof internalZod.enum;
  readonly nativeEnum: typeof internalZod.nativeEnum;
  readonly object: typeof internalZod.object;
  readonly strictObject: typeof internalZod.strictObject;
  readonly looseObject: typeof internalZod.looseObject;
  readonly array: typeof internalZod.array;
  readonly tuple: typeof internalZod.tuple;
  readonly union: typeof internalZod.union;
  readonly discriminatedUnion: typeof internalZod.discriminatedUnion;
  readonly intersection: typeof internalZod.intersection;
  readonly record: typeof internalZod.record;
  readonly partialRecord: typeof internalZod.partialRecord;
  readonly lazy: typeof internalZod.lazy;
  readonly promise: typeof internalZod.promise;
  readonly preprocess: typeof internalZod.preprocess;
  readonly custom: typeof internalZod.custom;
  readonly instanceof: typeof internalZod.instanceof;
  readonly optional: typeof internalZod.optional;
  readonly nullable: typeof internalZod.nullable;
  readonly nullish: typeof internalZod.nullish;
  readonly null: typeof internalZod.null;
  readonly undefined: typeof internalZod.undefined;
  readonly unknown: typeof internalZod.unknown;
  readonly any: typeof internalZod.any;
  readonly never: typeof internalZod.never;
  readonly void: typeof internalZod.void;
  readonly coerce: typeof internalZod.coerce;
  readonly parse: typeof internalZod.parse;
  readonly parseAsync: typeof internalZod.parseAsync;
  readonly safeParse: typeof internalZod.safeParse;
  readonly safeParseAsync: typeof internalZod.safeParseAsync;
}

export const z: CodepotZodCompatibility = {
  string: internalZod.string,
  number: internalZod.number,
  boolean: internalZod.boolean,
  bigint: internalZod.bigint,
  date: internalZod.date,
  literal: internalZod.literal,
  enum: internalZod.enum,
  nativeEnum: internalZod.nativeEnum,
  object: internalZod.object,
  strictObject: internalZod.strictObject,
  looseObject: internalZod.looseObject,
  array: internalZod.array,
  tuple: internalZod.tuple,
  union: internalZod.union,
  discriminatedUnion: internalZod.discriminatedUnion,
  intersection: internalZod.intersection,
  record: internalZod.record,
  partialRecord: internalZod.partialRecord,
  lazy: internalZod.lazy,
  promise: internalZod.promise,
  preprocess: internalZod.preprocess,
  custom: internalZod.custom,
  instanceof: internalZod.instanceof,
  optional: internalZod.optional,
  nullable: internalZod.nullable,
  nullish: internalZod.nullish,
  null: internalZod.null,
  undefined: internalZod.undefined,
  unknown: internalZod.unknown,
  any: internalZod.any,
  never: internalZod.never,
  void: internalZod.void,
  coerce: internalZod.coerce,
  parse: internalZod.parse,
  parseAsync: internalZod.parseAsync,
  safeParse: internalZod.safeParse,
  safeParseAsync: internalZod.safeParseAsync,
};

export namespace z {
  export type infer<TSchema extends z4.$ZodType> = z4.output<TSchema>;
  export type input<TSchema extends z4.$ZodType> = z4.input<TSchema>;
  export type output<TSchema extends z4.$ZodType> = z4.output<TSchema>;
  export type ZodTypeAny = z4.$ZodType & {
    safeParse(data: unknown): { readonly success: boolean; readonly data?: unknown };
    parse(data: unknown): unknown;
  };
  export type ZodType<TOutput = unknown, TInput = unknown> = z4.$ZodType<TOutput, TInput> & {
    safeParse(data: unknown): { readonly success: boolean; readonly data?: TOutput };
    parse(data: TInput): TOutput;
  };
  export type ZodIssue = z4.$ZodIssue;
  export type ZodError = z4.$ZodError;
}

export const ZOD_COMPATIBILITY_FEATURES: readonly string[] = Object.freeze(Object.keys(z).sort());
