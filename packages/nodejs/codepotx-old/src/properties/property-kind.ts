export const PropertyKind = {
  shared: 'shared',
  entity: 'entity',
  forRef: 'for-ref',
} as const;

export type PropertyKind = (typeof PropertyKind)[keyof typeof PropertyKind];
