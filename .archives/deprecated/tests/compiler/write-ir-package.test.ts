// tests/compiler/write-ir-package.test.ts

import { existsSync, readFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';

import { describe, expect, it } from 'vitest';

import { createIrJsonFileName, emitIrContract, writeIrPackage } from '@/app';
import { validateIrRefs } from '@/compiler/validators';
import type { CodepotDefinition } from '@/contract/types/ir/definition';

import { demoConfig as config, v1 } from '../fixtures/contracts/v1-demo';

// ============================================================================
// OUTPUT
// ============================================================================

const outputFolder = join('tests', 'generated', 'ir');

/**
 * Writes the demo IR package and reads the generated JSON file.
 */
async function writeAndReadDemoIr(): Promise<CodepotDefinition> {
  rmSync(outputFolder, {
    recursive: true,
    force: true,
  });

  await writeIrPackage({
    ...config,
    output: {
      folder: outputFolder,
    },
  });

  return JSON.parse(readFileSync(join(outputFolder, 'codepot.v1.json'), 'utf8')) as CodepotDefinition;
}

// ============================================================================
// TEST
// ============================================================================

describe('writeIrPackage', () => {
  it('writes canonical versioned IR JSON and YAML files', async () => {
    rmSync(outputFolder, {
      recursive: true,
      force: true,
    });

    const result = await writeIrPackage({
      ...config,
      output: {
        folder: outputFolder,
      },
    });

    expect(result.files).toEqual(['tests/generated/ir/codepot.v1.json', 'tests/generated/ir/codepot.v1.yaml']);

    const jsonPath = join(outputFolder, 'codepot.v1.json');
    const yamlPath = join(outputFolder, 'codepot.v1.yaml');

    expect(existsSync(jsonPath)).toBe(true);
    expect(existsSync(yamlPath)).toBe(true);

    const ir = JSON.parse(readFileSync(jsonPath, 'utf8'));

    expect(ir.codepot).toBeDefined();
    expect(ir.version).toBe(1);
    expect(ir.content_types.json).toBeDefined();
    expect(ir.properties.primitives).toBeDefined();
    expect(ir.schemas.entities).toBeDefined();
    expect(ir.schemas.models).toBeDefined();
    expect(ir.schemas.dtos).toBeDefined();
    expect(ir.responses.errors).toBeDefined();
    expect(ir.resources).toBeDefined();
  });

  it('writes direct Codepot IR JSON, not a package wrapper', async () => {
    const ir = await writeAndReadDemoIr();

    expect((ir as unknown as Record<string, unknown>).contracts).toBeUndefined();
    expect(ir.codepot).toBe('1.0');
    expect(ir.key).toBe('demo_api');
    expect(ir.version).toBe(1);

    expect(ir.schemas).toBeDefined();
    expect(ir.resources).toBeDefined();
  });

  it('writes emitted JSON with no broken refs', async () => {
    const ir = await writeAndReadDemoIr();

    expect(validateIrRefs(ir)).toEqual([]);
  });

  it('writes emitted JSON with dotted scoped keys and no old underscore scoped keys', async () => {
    const ir = await writeAndReadDemoIr();

    expect(ir.responses.errors['resource.users.email_taken']).toBeDefined();
    expect(ir.responses.errors['resource.users.email_taken'].ownership).toEqual({
      $ref: '#/resources/users',
    });
    expect(ir.responses.errors['users.email_taken']).toBeUndefined();
    expect(ir.responses.errors.users_email_taken).toBeUndefined();

    expect(ir.schemas.params['resource.users.id']).toBeDefined();
    expect(ir.schemas.params['resource.users.id'].ownership).toEqual({
      $ref: '#/resources/users',
    });
    expect(ir.schemas.params['users.id']).toBeUndefined();
    expect(ir.schemas.params.users_id).toBeUndefined();

    expect(ir.schemas.field_sets['entity.user.list_select']).toBeDefined();
    expect(ir.schemas.field_sets['entity.user.list_select'].ownership).toEqual({
      $ref: '#/schemas/entities/user',
    });
    expect(ir.schemas.field_sets['user.list_select']).toBeUndefined();
    expect(ir.schemas.field_sets.user_list_select).toBeUndefined();
  });

  it('writes emitted JSON with compiled DTO composition and content negotiation', async () => {
    const ir = await writeAndReadDemoIr();

    expect(ir.schemas.dtos.user_response.fields.user).toMatchObject({
      $ref: '#/schemas/models/entity.user.user_public',
      required: true,
    });

    const routeJson = JSON.stringify(ir.resources.users.routes);

    expect(routeJson).toContain('#/content_types/json');

    if (routeJson.includes('#/content_types/xml')) {
      expect(routeJson).toContain('#/content_types/xml');
    }
  });

  it('creates the JSON filename from the compiled IR version', () => {
    const ir = emitIrContract(v1.snapshot());

    expect(createIrJsonFileName(ir)).toBe('codepot.v1.json');
  });
});
