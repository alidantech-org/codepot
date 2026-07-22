import { describe, expect, it } from 'vitest';

import { emitAuthoringDebugPackage, serializeAuthoringDebugPackageJson, serializeAuthoringDebugPackageYaml } from '@/app';
import { demoConfig } from '../fixtures/contracts/v1-demo';

describe('debug authoring output', () => {
  it('emits collected authoring intent', () => {
    const output = emitAuthoringDebugPackage(demoConfig);

    expect(output.contracts).toHaveLength(1);

    const json = JSON.stringify(output);

    expect(json).toContain('"key":"demo_api"');
    expect(json).toContain('"version":1');

    expect(json).toContain('property:primitive:id');
    expect(json).toContain('property:primitive:displayName');
    expect(json).toContain('property:primitive:email');
    expect(json).toContain('property:enum:UserRole');

    expect(json).toContain('schema:entity:User:field:name');
    expect(json).toContain('schema:entity:User:field:role');
    expect(json).toContain('schema:model:User:public');
    expect(json).toContain('error:unauthorized');

    expect(json).toContain('security:credential:bearer');
    expect(json).toContain('security:principal:user');
    expect(json).toContain('security:policy:tenantAdmin');

    expect(json).toContain('"users"');
    expect(json).toContain('"listUsers"');

    expect(json).toContain('"routes"');

    expect(json).not.toContain('"$ref"');
    expect(json).not.toContain('#/schemas');
    expect(json).not.toContain('#/security');

    // Verify operations do not exist in authoring (they are compiler output)
    const contract = output.contracts[0] as any;
    expect(contract.resources.users.operations).toBeUndefined();
    expect(contract.resources.users.routes.listUsers).toBeDefined();
    expect(contract.resources.users.routes.createUser).toBeDefined();
  });

  it('emits promotable inline properties', () => {
    const output = emitAuthoringDebugPackage(demoConfig);

    expect(output.contracts).toHaveLength(1);

    const json = JSON.stringify(output);

    // Verify inline property source.mode exists
    expect(json).toContain('"mode":"inline"');

    // Verify property ref source.mode exists
    expect(json).toContain('"mode":"ref"');

    // Verify composite inline properties have promotion hints
    expect(json).toContain('"ownerKind":"composite"');

    // Verify entity inline properties have promotion hints
    expect(json).toContain('"ownerKind":"entity"');

    // Verify suggested keys are generated
    expect(json).toContain('"suggestedKey":"composite.inline_money.amount"');
    expect(json).toContain('"suggestedKey":"entity.user.nickname"');

    // Verify direct primitive members are no longer nested directly
    expect(json).not.toContain('"amount":{"kind":"primitive"');

    // Verify old confusing source modes no longer exist
    expect(json).not.toContain('"sourceMode"');
    expect(json).not.toContain('"kind":"property_ref"');
    expect(json).not.toContain('"kind":"inline_property"');
    expect(json).not.toContain('"kind":"property"');
  });

  it('applies meaningful defaults without verbose false noise', () => {
    const output = emitAuthoringDebugPackage(demoConfig);

    expect(output.contracts).toHaveLength(1);

    const contract = output.contracts[0] as any;
    const user = contract.schemas.entities.User;
    const billingLimit = user.fields.billingLimit.options;

    // Verify meaningful defaults are applied
    expect(billingLimit.required).toBe(false);
    expect(billingLimit.visibility.read).toBe('internal');
    expect(billingLimit.persistence.mode).toBe('stored');

    // Verify false noise is omitted
    expect(billingLimit.nullable).toBeUndefined();
    expect(billingLimit.array).toBeUndefined();

    // Verify relation defaults
    const posts = contract.schemas.entities.Tag.fields.posts.options;

    expect(posts.required).toBe(true);
    expect(posts.array).toBe(true);
    expect(posts.visibility.read).toBe('internal');
    expect(posts.persistence.mode).toBe('virtual');

    // Verify explicit values are preserved
    const email = user.fields.email.options;

    expect(email.capability.select).toBe(false);
    expect(email.visibility.sensitive).toBe(true);
  });

  it('refs do not contain name property', () => {
    const output = emitAuthoringDebugPackage(demoConfig);

    expect(output.contracts).toHaveLength(1);

    const json = JSON.stringify(output);

    // Ensure no ref contains "name" property (only key)
    // This regex looks for "name":" followed by the same value as key to avoid false positives
    expect(json).not.toMatch(/"name":"[^"]*"[,}]/);

    // Verify a specific ref structure
    const contract = output.contracts[0] as any;
    const user = contract.schemas.entities.User;
    const nameFieldRef = user.fields.name.source.ref;

    expect(nameFieldRef).toHaveProperty('id');
    expect(nameFieldRef).toHaveProperty('kind');
    expect(nameFieldRef).toHaveProperty('key');
    expect(nameFieldRef).not.toHaveProperty('name');
  });

  it('writes debug json string without compiled refs', () => {
    const json = serializeAuthoringDebugPackageJson(demoConfig);

    expect(json).toContain('"contracts"');
    expect(json).toContain('security:credential:bearer');
    expect(json).not.toContain('"$ref"');
    expect(json).not.toContain('#/schemas');
  });

  it('writes debug yaml string without compiled refs', () => {
    const yaml = serializeAuthoringDebugPackageYaml(demoConfig);

    expect(yaml).toContain('contracts:');
    expect(yaml).toContain('security:credential:bearer');
    expect(yaml).not.toContain('$ref');
    expect(yaml).not.toContain('#/schemas');
  });

  it('emits new security model with credentials, principals, and policies', () => {
    const output = emitAuthoringDebugPackage(demoConfig);
    const contract = output.contracts[0] as any;
    const security = contract.security;

    // Verify credentials
    expect(security.credentials).toBeDefined();
    expect(security.credentials.bearer).toBeDefined();
    expect(security.credentials.bearer.source).toBe('header');
    expect(security.credentials.bearer.key).toBe('authorization');
    expect(security.credentials.bearer.format).toBe('bearer');
    expect(security.credentials.bearer.valueType.id).toBe('property:primitive:text');

    expect(security.credentials.session).toBeDefined();
    expect(security.credentials.session.source).toBe('cookie');
    expect(security.credentials.session.key).toBe('session_id');
    expect(security.credentials.session.format).toBe('session');

    // Verify principals
    expect(security.principals).toBeDefined();
    expect(security.principals.user).toBeDefined();
    expect(security.principals.user.id.id).toBe('schema:entity:BaseEntity:field:id');
    expect(security.principals.user.roles.id).toBe('schema:entity:User:field:roles');
    expect(security.principals.user.status.id).toBe('schema:entity:User:field:status');

    expect(security.principals.tenant).toBeDefined();
    expect(security.principals.tenant.id.id).toBe('schema:entity:BaseEntity:field:id');
    expect(security.principals.tenant.ownerId.id).toBe('schema:entity:Tenant:field:ownerId');

    // Verify policies
    expect(security.policies).toBeDefined();
    expect(security.policies.public).toBeDefined();
    expect(security.policies.public.mode).toBe('public');

    expect(security.policies.authenticated).toBeDefined();
    expect(security.policies.authenticated.mode).toBe('protected');

    expect(security.policies.tenantMember).toBeDefined();
    expect(security.policies.tenantMember.mode).toBe('protected');
    expect(security.policies.tenantMember.credential.id).toBe('security:credential:bearer');
    expect(security.policies.tenantMember.principals.user.id).toBe('security:principal:user');
    expect(security.policies.tenantMember.principals.tenant.id).toBe('security:principal:tenant');
    expect(security.policies.tenantMember.roles).toEqual(['owner', 'admin', 'member']);
    expect(security.policies.tenantMember.intent).toBe('tenant_role');

    expect(security.policies.tenantAdmin).toBeDefined();
    expect(security.policies.tenantAdmin.mode).toBe('protected');
    expect(security.policies.tenantAdmin.credential.id).toBe('security:credential:bearer');
    expect(security.policies.tenantAdmin.principals.user.id).toBe('security:principal:user');
    expect(security.policies.tenantAdmin.principals.tenant.id).toBe('security:principal:tenant');
    expect(security.policies.tenantAdmin.roles).toEqual(['owner', 'admin']);
    expect(security.policies.tenantAdmin.permissions).toEqual(['users.read', 'users.write']);
    expect(security.policies.tenantAdmin.intent).toBe('tenant_role');
  });

  it('resources accept both inline security policy and policy refs', () => {
    const output = emitAuthoringDebugPackage(demoConfig);
    const contract = output.contracts[0] as any;

    const users = contract.resources.users;
    expect(users.defaults.security).toBeDefined();
    expect(users.defaults.security.mode).toBe('protected');

    const tenants = contract.resources.tenants;
    expect(tenants.defaults.security).toBeDefined();
    expect(tenants.defaults.security.id).toBe('security:policy:tenantMember');
    expect(tenants.defaults.security.kind).toBe('security.policy');
  });

  it('adds json content by default when body has schema', () => {
    const output = emitAuthoringDebugPackage(demoConfig);
    const contract = output.contracts[0] as any;
    const users = contract.resources.users;

    expect(users.routes.createUser.body.content).toEqual([
      {
        key: 'json',
        type: 'application/json',
        strategy: 'json',
      },
    ]);
  });

  it('adds json content by default when output has schema', () => {
    const output = emitAuthoringDebugPackage(demoConfig);
    const contract = output.contracts[0] as any;
    const users = contract.resources.users;

    expect(users.routes.listUsers.output.content).toEqual([
      {
        key: 'json',
        type: 'application/json',
        strategy: 'json',
      },
    ]);
  });

  it('does not add json content for no-content output', () => {
    const output = emitAuthoringDebugPackage(demoConfig);
    const contract = output.contracts[0] as any;
    const users = contract.resources.users;

    expect(users.routes.deleteUser.output.status).toBe(204);
    expect(users.routes.deleteUser.output.content).toBeUndefined();
  });

  it('preserves explicit multipart content', () => {
    const output = emitAuthoringDebugPackage(demoConfig);
    const contract = output.contracts[0] as any;
    const users = contract.resources.users;

    expect(users.routes.uploadAvatar.body.content).toEqual([
      {
        key: 'multipart',
        type: 'multipart/form-data',
        strategy: 'multipart',
      },
    ]);
  });

  it('preserves multiple explicit output content types', () => {
    const output = emitAuthoringDebugPackage(demoConfig);
    const contract = output.contracts[0] as any;
    const users = contract.resources.users;

    expect(users.routes.feedXml.output.content).toEqual([
      {
        key: 'json',
        type: 'application/json',
        strategy: 'json',
      },
      {
        key: 'xml',
        type: 'application/xml',
        strategy: 'xml',
      },
    ]);
  });

  it('content descriptors include key, type, and strategy', () => {
    const output = emitAuthoringDebugPackage(demoConfig);
    const contract = output.contracts[0] as any;
    const users = contract.resources.users;

    // Verify content descriptor structure
    const jsonContent = users.routes.createUser.body.content[0];
    expect(jsonContent).toHaveProperty('key');
    expect(jsonContent).toHaveProperty('type');
    expect(jsonContent).toHaveProperty('strategy');
  });

  it('old security graph is gone', () => {
    const output = emitAuthoringDebugPackage(demoConfig);
    const contract = output.contracts[0] as any;
    const security = contract.security;

    // Verify old concepts are gone
    expect(security.schemes).toBeUndefined();
    expect(security.auth).toBeUndefined();
    expect(security.roleSources).toBeUndefined();
    expect(security.roleSets).toBeUndefined();
    expect(security.contexts).toBeUndefined();
    expect(security.guards).toBeUndefined();
  });
});
