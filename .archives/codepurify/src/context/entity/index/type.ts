import { ArrayChildContext } from "@/context/global/array/type";
import { NameContext } from "@/context/global/name/type";
import { FieldContext } from "../field/type";

export type IndexContext = {
  key: string;

  name: NameContext;

  field: {
    array: {
      all: ArrayChildContext<FieldContext>;
    };
  };

  flag: {
    is_unique: boolean;
    is_normal: boolean;
    is_composite: boolean;
    is_single_field: boolean;
    has_fields: boolean;
  };
};
