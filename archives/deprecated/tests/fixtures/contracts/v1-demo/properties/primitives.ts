import { property } from '@/index';

import { properties } from '../version';


// ============================================================================
// GLOBAL PRIMITIVES
// ============================================================================

export const primitives = properties.primitives({
  // Identity primitives
  id: property.uuid(),
  uuid: property.uuid(),
  slug: property.string().minLength(3).maxLength(100).pattern('^[a-z0-9-]+$'),
  externalId: property.string().minLength(1).maxLength(100),

  // Time primitives
  dateTime: property.dateTime(),
  date: property.date(),
  time: property.time(),
  durationSeconds: property.integer().min(0),

  // Text primitives
  text: property.string(),
  shortText: property.string().minLength(1).maxLength(50),
  longText: property.string().maxLength(5000),
  title: property.string().minLength(2).maxLength(120),
  description: property.string().maxLength(500),
  message: property.string().maxLength(1000),
  richText: property.string().maxLength(10000),

  // Contact primitives
  email: property.email(),
  phoneNumber: property.string().minLength(10).maxLength(20),
  url: property.string().format('uri'),

  // Number primitives
  integer: property.integer(),
  positiveInteger: property.integer().min(0),
  decimal: property.number(),
  percentage: property.number().min(0).max(100),

  // Money primitives
  moneyAmount: property.number().min(0),
  currencyCode: property.string().minLength(3).maxLength(3),

  // File primitives
  fileName: property.string().minLength(1).maxLength(180),
  mimeType: property.string().minLength(3).maxLength(100),
  fileSize: property.integer().min(0),
  checksum: property.string().minLength(32).maxLength(64),

  // Security primitives
  token: property.string().minLength(20).maxLength(500),
  apiKey: property.string().minLength(32).maxLength(100),
  ipAddress: property.string().pattern('^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$'),
  userAgent: property.string().maxLength(500),

  // Flag primitives
  boolean: property.boolean(),

  // Legacy primitives (kept for backward compatibility)
  displayName: property.string().minLength(2).maxLength(80),
  bio: property.string().maxLength(500),
});