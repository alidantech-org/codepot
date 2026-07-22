import { property } from '@/index';

import { properties } from '../version';
import { primitives } from './primitives';



// ============================================================================
// GLOBAL COMPOSITES
// ============================================================================

export const composites = properties.composites({
  // Money composites
  money: property.composite({
    amount: primitives.ref.moneyAmount,
    currency: primitives.ref.currencyCode,
  }),

  inlineMoney: property.composite({
    amount: property.number().min(0),
    currency: property.string().minLength(3).maxLength(3),
  }),

  // Address composite with inline properties
  address: property.composite({
    street: property.string().minLength(1).maxLength(200),
    city: property.string().minLength(1).maxLength(100),
    state: property.string().minLength(1).maxLength(100),
    postalCode: property.string().minLength(1).maxLength(20),
    country: property.string().minLength(2).maxLength(2),
  }),

  // Geo point composite
  geoPoint: property.composite({
    latitude: property.number().min(-90).max(90),
    longitude: property.number().min(-180).max(180),
  }),

  // File asset composite with inline properties
  fileAsset: property.composite({
    fileName: property.string().minLength(1).maxLength(180),
    mimeType: property.string().minLength(3).maxLength(100),
    fileSize: property.integer().min(0),
    checksum: property.string().minLength(32).maxLength(64),
    url: property.string().format('uri'),
  }),

  // Audit stamp composite
  auditStamp: property.composite({
    createdAt: primitives.ref.dateTime,
    createdBy: primitives.ref.id,
    updatedAt: primitives.ref.dateTime,
    updatedBy: primitives.ref.id,
  }),

  // Date range composite
  dateRange: property.composite({
    startDate: primitives.ref.date,
    endDate: primitives.ref.date,
  }),

  // Percentage breakdown composite
  percentageBreakdown: property.composite({
    category: property.string().minLength(1).maxLength(50),
    percentage: property.number().min(0).max(100),
  }),
});