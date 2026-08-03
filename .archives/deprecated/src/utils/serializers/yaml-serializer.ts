import { stringify } from 'yaml';

export function serializeYaml(value: unknown): string {
  return stringify(value);
}
