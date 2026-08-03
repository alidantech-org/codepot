import { ArrayChildContext } from "@/context/global/array/type";
import { NameContext } from "@/context/global/name/type";

export type TransitionStateContext = {
  key: string;

  name: NameContext;

  target: {
    array: {
      all: ArrayChildContext<NameContext>;
    };
  };

  flag: {
    is_terminal: boolean;

    has_targets: boolean;
  };
};

export type TransitionContext = {
  key: string;

  name: NameContext;

  initial: NameContext | null;

  terminal: {
    array: {
      all: ArrayChildContext<NameContext>;
    };
  };

  state: {
    array: {
      all: ArrayChildContext<TransitionStateContext>;
    };
  };

  flag: {
    has_initial: boolean;

    has_terminal: boolean;

    has_states: boolean;
  };
};
