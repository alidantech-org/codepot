import type {
  RuntimeFeature,
  RuntimeFeatureQuery,
} from '@/contract/index';

export function selectRuntimeFeatures(
  features: readonly RuntimeFeature[],
  query: RuntimeFeatureQuery,
): readonly RuntimeFeature[] {
  return features.filter((feature) => {
    if (query.layer && feature.layer !== query.layer) return false;
    if (query.capability && !feature.capabilities.includes(query.capability)) return false;
    return true;
  });
}
