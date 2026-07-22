import type {
  AuthoringPort,
  ClockPort,
  EventBusPort,
  GenerationPort,
  IdPort,
  RuntimeFeature,
  TemplatingPort,
} from '@/contract/index';

export interface RuntimeDependencies {
  readonly authoring: AuthoringPort;
  readonly templating: TemplatingPort;
  readonly generation: GenerationPort;
  readonly events: EventBusPort;
  readonly clock: ClockPort;
  readonly ids: IdPort;
  readonly features?: readonly RuntimeFeature[];
}
