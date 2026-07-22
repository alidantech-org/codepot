export function toSchemaName(...parts: Array<string | undefined>): string {
  return parts
    .filter((part): part is string => !!part)
    .flatMap(splitName)
    .map(capitalize)
    .join('');
}

function splitName(value: string): string[] {
  return value
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .split(/[^a-zA-Z0-9]+/)
    .filter(Boolean);
}

function capitalize(value: string): string {
  if (!value) return value;

  return value.charAt(0).toUpperCase() + value.slice(1);
}
