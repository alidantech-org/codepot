// src/contract/constants/entity-field-sets.ts

import { valueObject } from './values';

export const EntityFieldSetNameValues = [
  'all',
  'scalar',
  'relation',

  'readable',
  'writable',
  'selectable',
  'sortable',
  'filterable',

  'public',
  'internal',
  'secret',
  'sensitive',
  'redacted',

  'persisted',
  'virtual',
  'computed',
  'generated',
  'immutable',

  'create',
  'patch',
  'read',
  'list',
  'summary',
  'option',

  'listSelect',
  'listSort',
  'listFilter',

  'publicListSelect',
  'publicListSort',
  'publicListFilter',

  'adminListSelect',
  'adminListSort',
  'adminListFilter',
] as const;

export const EntityFieldSetName = valueObject(EntityFieldSetNameValues);

export type EntityFieldSetName = (typeof EntityFieldSetNameValues)[number];
