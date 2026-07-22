import assert from 'node:assert/strict';
import test from 'node:test';

import {
  SchemaKind,
  schema,
  z,
  ZOD_COMPATIBILITY_FEATURES,
} from '../src/index';

test('z compatibility preserves actual old contract chains', () => {
  const name = z.string().min(1).max(100);
  const status = z.enum(['active', 'disabled', 'pending'] as const);
  const page = z.number().int().positive().max(10_000);

  assert.equal(name.safeParse('Codepot').success, true);
  assert.equal(name.safeParse('').success, false);
  assert.equal(status.safeParse('active').success, true);
  assert.equal(status.safeParse('unknown').success, false);
  assert.equal(page.safeParse(1).success, true);
  assert.equal(page.safeParse(-1).success, false);
});

test('schema combines preferred constructors with preserved Codepot helpers', () => {
  const email = schema.string().email();
  assert.equal(email.safeParse('dev@alidantech.org').success, true);

  const primitive = schema.primitive(schema.string().datetime());
  assert.equal(primitive.kind, SchemaKind.primitive);

  const literal = schema.literal('ready');
  assert.equal(literal.kind, SchemaKind.literal);
  assert.equal(literal.value, 'ready');

  const zodLiteral = z.literal('ready');
  assert.equal(zodLiteral.safeParse('ready').success, true);
  assert.equal(zodLiteral.safeParse('other').success, false);
});

test('curated Zod surface is explicit and stable', () => {
  assert.equal(ZOD_COMPATIBILITY_FEATURES.includes('string'), true);
  assert.equal(ZOD_COMPATIBILITY_FEATURES.includes('enum'), true);
  assert.equal(ZOD_COMPATIBILITY_FEATURES.includes('record'), true);
  assert.equal(Object.isFrozen(schema), true);
});
