import { ArrayChildContext } from '../global/array/type';
import { NameContext } from '../global/name/type';
import { TemplateContext } from '../global/template/type';
import { CheckContext } from './check/type';
import { FieldContext } from './field/type';
import { IndexContext } from './index/type';
import { RelationContext } from './relation/type';
import { TransitionContext } from './transition/type';

export type EntityContext = {
  key: string;
  group_key: string;

  name: NameContext;

  field: {
    array: {
      all: ArrayChildContext<FieldContext>;
      scalar: ArrayChildContext<FieldContext>;
      enum: ArrayChildContext<FieldContext>;
      boolean: ArrayChildContext<FieldContext>;
      foreign: ArrayChildContext<FieldContext>;
      nullable: ArrayChildContext<FieldContext>;
      required: ArrayChildContext<FieldContext>;
      queryable: ArrayChildContext<FieldContext>;
      mutable: ArrayChildContext<FieldContext>;
      system: ArrayChildContext<FieldContext>;
      api: ArrayChildContext<FieldContext>;
    };
  };

  relation: {
    array: {
      all: ArrayChildContext<RelationContext>;
      one_to_many: ArrayChildContext<RelationContext>;
      many_to_one: ArrayChildContext<RelationContext>;
      one_to_one: ArrayChildContext<RelationContext>;
      many_to_many: ArrayChildContext<RelationContext>;
    };
  };

  index: {
    array: {
      all: ArrayChildContext<IndexContext>;
      unique: ArrayChildContext<IndexContext>;
      normal: ArrayChildContext<IndexContext>;
    };
  };

  check: {
    array: {
      all: ArrayChildContext<CheckContext>;
    };
  };

  transition: {
    array: {
      all: ArrayChildContext<TransitionContext>;
    };
  };

  template: {
    array: {
      all: ArrayChildContext<TemplateContext>;
      entity: ArrayChildContext<TemplateContext>;
      resource: ArrayChildContext<TemplateContext>;
    };
  };

  flag: {
    has_base: boolean;
    has_workflows: boolean;
    has_fields: boolean;
    has_relations: boolean;
    has_indexes: boolean;
    has_checks: boolean;
    has_transitions: boolean;
    has_templates: boolean;
    uses_timestamps: boolean;
    uses_audit: boolean;
  };
};
