import { ArrayChildContext } from "../array/type";
import { CasingContext, NameUnitContext, NameContext } from "../name/type";

export type PathContext = {
  original: string;

  casing: CasingContext;

  array: {
    parts: ArrayChildContext<PathPartContext>;
    directories: ArrayChildContext<PathPartContext>;
    characters: ArrayChildContext<NameUnitContext>;
  };
};

export type PathPartContext = {
  original: string;

  name: NameContext;
};

export type TemplateContext = {
  key: string;

  name: NameContext;

  kind: NameContext;

  description: string | null;

  root_directory: PathContext;

  template_path: PathContext;

  output: {
    folder: {
      array: {
        all: ArrayChildContext<PathPartContext>;
      };
    };

    file: {
      base: NameContext;

      prefix: NameContext | null;

      suffix: NameContext | null;

      extension: NameContext;

      full_name: NameContext;
    };

    full_path: PathContext;
  };

  flag: {
    has_description: boolean;

    has_prefix: boolean;

    has_suffix: boolean;

    is_entity: boolean;

    is_resource: boolean;
  };
};