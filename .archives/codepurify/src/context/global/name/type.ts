import { ArrayChildContext } from "../array/type";

export type CasingContext = {
  camel: string;
  pascal: string;
  snake: string;
  kebab: string;
  dot: string;
  slash: string;
  path: string;
  constant: string;
  lower: string;
  upper: string;
  title: string;
  train: string;
};

export type NameUnitContext = {
  original: string;
  casing: CasingContext;
};

export type NameArraysContext = {
  parts: ArrayChildContext<NameUnitContext>;
  words: ArrayChildContext<NameUnitContext>;
  characters: ArrayChildContext<NameUnitContext>;
};

export type NameContext = {
  original: string;
  casing: CasingContext;
  array: NameArraysContext;
};
