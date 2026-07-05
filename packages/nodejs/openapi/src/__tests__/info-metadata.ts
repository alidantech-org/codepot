import assert from 'node:assert/strict';
import { z } from 'zod';
import { CODEGEN_EXTENSION_KEY, HttpMethod, compileOpenApi, defineVersionContract, normalizeInfo } from '../index.js';

const reusableInfo = {
  apiKeySecurity: {
    security: ['Never store API keys in raw form.', 'Expose only keyPrefix.'],
    implement: ['Return the raw secret only once.'],
  },
};

assert.deepEqual(
  normalizeInfo((i) =>
    i
      .use(reusableInfo.apiKeySecurity)
      .security('Never store API keys in raw form.')
      .custom('tenantSafety', ['Always scope reads by tenant context.']),
  ),
  {
    security: ['Never store API keys in raw form.', 'Expose only keyPrefix.'],
    implement: ['Return the raw secret only once.'],
    tenantSafety: ['Always scope reads by tenant context.'],
  },
);

assert.deepEqual(
  normalizeInfo([
    reusableInfo.apiKeySecurity,
    {
      warn: 'Revoked keys must not authenticate requests.',
      billing: ['Billing-specific note.'],
    },
  ]),
  {
    security: ['Never store API keys in raw form.', 'Expose only keyPrefix.'],
    implement: ['Return the raw secret only once.'],
    warn: ['Revoked keys must not authenticate requests.'],
    billing: ['Billing-specific note.'],
  },
);

assert.throws(() => normalizeInfo({ explain: [123 as unknown as string] }), /only accepts strings/);

const v1 = defineVersionContract({
  info: {
    title: 'Info API',
    version: '1.0.0',
  },
});

const sharedProps = v1.defineProperties('Shared', {
  uuid: z.string().uuid(),
  token: z.string(),
});

const access = v1.defineAccess({
  authenticated: {
    context: null,
    info: {
      auth: 'Requires a valid session.',
    },
  },
});

const apps = v1
  .defineResource({
    name: 'apps',
    route: '/apps',
    access: access.ref.authenticated,
    info: {
      explain: 'Platform apps resource.',
    },
  })
  .info((i) => i.important('Resource info can be attached fluently.'));

const schemas = apps.defineSchemas({
  App: {
    id: sharedProps.ref.uuid,
    keyPrefix: sharedProps.ref.token,
  },
});

apps.defineEntities({
  App: {
    schema: schemas.ref.App,
    store: 'apps',
    backend: {
      keyHash: sharedProps.ref.token,
    },
    info: reusableInfo.apiKeySecurity,
    fields: {
      keyPrefix: ($) => $.readonly().managed().info((i) => i.security('Only expose a key prefix.')),
      keyHash: ($) => $.select(false).edit(false).info({ security: 'Never expose keyHash.' }),
    },
  },
});

const responses = apps.defineSchemas({
  AppResponse: {
    app: schemas.ref.App,
  },
});

const appRoutes = apps.defineRoutes({
  routes: {
    createApp: {
      method: HttpMethod.post,
      path: '/',
      response: responses.ref.AppResponse,
      info: {
        implement: 'Create app records transactionally.',
      },
    },
  },
});

const frontend = v1
  .defineFrontend({
    name: 'admin',
    title: 'Admin',
    info: {
      explain: 'Admin frontend.',
    },
  })
  .info((i) => i.ux('Use clear empty states.'));

const components = frontend
  .defineComponents()
  .components((c) => ({
    AppsTable: c
      .component()
      .props({
        apps: schemas.ref.App.array(),
      })
      .uses({
        createApp: appRoutes.ref.createApp,
      })
      .info((i) => i.ux('Support loading state.')),
  })).ref;

frontend.defineScreens().screens((s) => ({
  AppsScreen: s
      .screen('/apps')
      .components({
        table: components.AppsTable,
      })
      .info({ implement: 'Render table below filters.' }),
}));

const result = compileOpenApi(v1.contract);
assert.equal(result.success, true);

const document = result.document;
const rootCodegen = document[CODEGEN_EXTENSION_KEY] as Record<string, any>;
assert.deepEqual(rootCodegen.resources.apps.info, {
  explain: ['Platform apps resource.'],
  important: ['Resource info can be attached fluently.'],
});
assert.deepEqual(rootCodegen.access.global.authenticated.info, {
  auth: ['Requires a valid session.'],
});
assert.deepEqual(rootCodegen.entities.apps.App.info, reusableInfo.apiKeySecurity);
assert.deepEqual(rootCodegen.entities.apps.App.fields.keyPrefix.info, {
  security: ['Only expose a key prefix.'],
});
assert.deepEqual(rootCodegen.entities.apps.App.fields.keyHash.info, {
  security: ['Never expose keyHash.'],
});
assert.deepEqual((document.paths['/apps'] as any).post[CODEGEN_EXTENSION_KEY].info, {
  implement: ['Create app records transactionally.'],
});
assert.deepEqual(rootCodegen.frontends.admin.info, {
  explain: ['Admin frontend.'],
  ux: ['Use clear empty states.'],
});
assert.deepEqual(rootCodegen.frontends.admin.components.AppsTable.info, {
  ux: ['Support loading state.'],
});
assert.deepEqual(rootCodegen.frontends.admin.screens.AppsScreen.info, {
  implement: ['Render table below filters.'],
});
