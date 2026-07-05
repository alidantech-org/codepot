export type InfoValue = string | readonly string[];

export type InfoObject = {
  readonly [category: string]: InfoValue | undefined;
};

export type InfoInput = InfoObject | readonly InfoObject[] | ((builder: InfoBuilder) => InfoBuilder);

export interface InfoBuilder {
  explain(value: InfoValue): InfoBuilder;
  implement(value: InfoValue): InfoBuilder;
  warn(value: InfoValue): InfoBuilder;
  important(value: InfoValue): InfoBuilder;
  notice(value: InfoValue): InfoBuilder;
  example(value: InfoValue): InfoBuilder;
  security(value: InfoValue): InfoBuilder;
  auth(value: InfoValue): InfoBuilder;
  access(value: InfoValue): InfoBuilder;
  privacy(value: InfoValue): InfoBuilder;
  validation(value: InfoValue): InfoBuilder;
  data(value: InfoValue): InfoBuilder;
  persistence(value: InfoValue): InfoBuilder;
  transaction(value: InfoValue): InfoBuilder;
  migration(value: InfoValue): InfoBuilder;
  performance(value: InfoValue): InfoBuilder;
  caching(value: InfoValue): InfoBuilder;
  testing(value: InfoValue): InfoBuilder;
  observability(value: InfoValue): InfoBuilder;
  errors(value: InfoValue): InfoBuilder;
  ux(value: InfoValue): InfoBuilder;
  accessibility(value: InfoValue): InfoBuilder;
  i18n(value: InfoValue): InfoBuilder;
  analytics(value: InfoValue): InfoBuilder;
  compliance(value: InfoValue): InfoBuilder;
  lifecycle(value: InfoValue): InfoBuilder;
  dependency(value: InfoValue): InfoBuilder;
  ai(value: InfoValue): InfoBuilder;
  todo(value: InfoValue): InfoBuilder;
  custom(category: string, value: InfoValue): InfoBuilder;
  use(input: InfoObject | readonly InfoObject[]): InfoBuilder;
  build(): NormalizedInfo;
}

export type NormalizedInfo = Record<string, readonly string[]>;
