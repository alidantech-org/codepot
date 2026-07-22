import { NameContext } from "@/context/global/name/type";
import { FieldContext } from "../field/type";
import { EntityContext } from "../type";

export type RelationContext = {
  key: string;

  name: NameContext;

  kind: NameContext;

  local_field: FieldContext | null;

  remote_field: FieldContext | null;

  local_entity: EntityContext | null;

  remote_entity: EntityContext | null;

  flag: {
    is_one_to_one: boolean;
    is_one_to_many: boolean;
    is_many_to_one: boolean;
    is_many_to_many: boolean;

    has_local_field: boolean;
    has_remote_field: boolean;

    is_nullable: boolean;

    has_cascade: boolean;

    has_on_delete: boolean;
  };

  config: {
    cascade: boolean;

    on_delete: string | null;
  };
};
