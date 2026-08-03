import { NameContext } from "@/context/global/name/type";
import { FieldContext } from "../field/type";

export type CheckContext = {
  key: string;

  name: NameContext;

  rule: {
    kind: NameContext;

    field: FieldContext | null;

    flag: {
      has_field: boolean;
    };
  };

  flag: {
    has_rule: boolean;
  };
};
