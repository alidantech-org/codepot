export type ArrayItemContext<TPayload extends object = object> = {
  index: number;
  number: number;

  flag: {
    is_first: boolean;
    is_last: boolean;
    is_even: boolean;
    is_odd: boolean;
  };
} & TPayload;

export type ArrayChildContext<TItem extends object = object> = {
  length: number;
  items: ArrayItemContext<TItem>[];
};

export type ArrayAccessorsContext<TChildren extends Record<string, ArrayChildContext<any>>> = TChildren;

export type FlagContext<TFlags extends Record<string, boolean>> = TFlags;
