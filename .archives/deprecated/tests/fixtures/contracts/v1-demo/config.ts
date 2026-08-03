import { defineCodepotConfig } from '@/index';

import { v1 } from './version';

// Ensure all authoring modules execute before config is exported.
import './properties';
import './entities';
import './relations';
import './dtos';
import './params';
import './errors';
import './security';
import './resources';

// ============================================================================
// EXPORT
// ============================================================================

export const demoConfig = defineCodepotConfig({
  contracts: [v1],
  output: {
    folder: 'tests/generated/debug',
    baseName: 'demo',
    formats: ['json', 'yaml'],
  },
});

export default demoConfig;
