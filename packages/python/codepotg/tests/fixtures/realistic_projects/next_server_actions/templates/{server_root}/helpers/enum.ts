/**
 * Converts enum wire values into human-readable labels for generated UI.
 */
export function enumLabel(value: string): string {
  return value
    .replace(/^[-+]/, '')
    .replace(/[_-]+/g, ' ')
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}
