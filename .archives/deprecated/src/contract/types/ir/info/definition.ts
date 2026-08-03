// src/contract/types/ir/info/definition.ts

import type { DefinitionItem } from '../definition';

// ============================================================================
// CONTACT
// ============================================================================

export interface ContactDefinition extends DefinitionItem {
  name?: string;
  url?: string;
  email?: string;
}

// ============================================================================
// LICENSE
// ============================================================================

export interface LicenseDefinition extends DefinitionItem {
  name: string;

  /**
   * SPDX identifier when available.
   * Example: MIT, Apache-2.0, GPL-3.0-only.
   */
  identifier?: string;

  url?: string;
}

// ============================================================================
// INFO LINKS
// ============================================================================

export interface InfoLinksDefinition {
  website?: string;
  docs?: string;
  support?: string;
  changelog?: string;
  status?: string;
  repository?: string;
}

// ============================================================================
// INFO
// ============================================================================

export interface InfoDefinition extends DefinitionItem {
  title: string;

  /**
   * Public API/product version.
   */
  version: string;

  /**
   * Optional short product/API summary.
   */
  summary?: string;

  terms_of_service?: string;

  contact?: ContactDefinition;

  license?: LicenseDefinition;

  /**
   * Useful product/project links.
   */
  links?: InfoLinksDefinition;
}
