import { CasingContext, NameContext } from '../../global/name/type';

export type KindContext = {
  original: string;
  casing: CasingContext;

  flag: {
    is_scalar: boolean;
    is_enum: boolean;
    is_relation: boolean;
    is_numeric: boolean;
    is_text: boolean;
  };
};

export type FieldContext = {
  name: NameContext;
  kind: KindContext;

  flag: {
    is_nullable: boolean;
    is_required: boolean;
    is_primary: boolean;
    is_unique: boolean;
    has_default: boolean;
  };
};
