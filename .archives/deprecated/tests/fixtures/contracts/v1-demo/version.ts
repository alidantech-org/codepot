// ============================================================================
// VERSION DEFINITION
// ============================================================================

import { defineVersionContract } from "@/contract";

export const v1 = defineVersionContract({
  key: 'demo_api',
  version: 1,
  info: { title: 'Demo API', version: '1.0.0' },
});

export const properties = v1.defineProperties();
export const schemas = v1.defineSchemas();
