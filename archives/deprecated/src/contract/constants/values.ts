// src/contract/constants/values.ts

export type ValueObject<TValues extends readonly string[]> = {
  readonly [K in TValues[number]]: K;
};

export function valueObject<const TValues extends readonly string[]>(
  values: TValues,
): ValueObject<TValues> {
  return Object.fromEntries(values.map((value) => [value, value])) as ValueObject<TValues>;
}
