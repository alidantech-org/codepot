import assert from 'node:assert/strict';
import { z } from 'zod';
import { CODEGEN_EXTENSION_KEY, HttpMethod, compileOpenApi, defineVersionContract } from '../index.js';

const v1 = defineVersionContract({
  info: {
    title: 'Frontend Test API',
    version: '1.0.0',
  },
});

const sharedProps = v1.defineProperties('Shared', {
  uuid: z.string().uuid(),
});

const apps = v1.defineResource({
  name: 'apps',
  route: '/platform/apps',
  folders: ['platform'],
});

const appProps = apps.defineProperties('App', {
  name: z.string(),
  status: z.enum(['active', 'disabled']),
});

const appProjectionSchemas = apps.defineSchemas({
  AppPartial: {
    id: sharedProps.ref.uuid,
    name: appProps.ref.name,
  },
  AppPublic: {
    id: sharedProps.ref.uuid,
    name: appProps.ref.name,
    status: appProps.ref.status,
  },
});

const appQuerySchemas = apps.defineSchemas({
  AppListQuery: {
    status: appProps.ref.status.optional(),
  },
});

const appRouteSchemas = apps.defineSchemas({
  AppRouteParams: {
    id: sharedProps.ref.uuid,
  },
});

const appBodySchemas = apps.defineSchemas({
  UpdateAppBody: appProjectionSchemas.ref.AppPublic.partial(),
});

const appResponseSchemas = apps.defineSchemas({
  AppsListResponse: {
    apps: appProjectionSchemas.ref.AppPartial.array(),
  },
});

const appRoutes = apps.defineRoutes({
  routes: {
    findApps: {
      method: HttpMethod.get,
      path: '/',
      response: appResponseSchemas.ref.AppsListResponse,
    },
    getAppById: {
      method: HttpMethod.get,
      path: '/:id',
      response: appProjectionSchemas.ref.AppPublic,
    },
    updateApp: {
      method: HttpMethod.patch,
      path: '/:id',
      body: appBodySchemas.ref.UpdateAppBody,
      response: appProjectionSchemas.ref.AppPublic,
    },
  },
});

const adminFrontend = v1.defineFrontend({
  name: 'admin',
  title: 'Admin',
  routePrefix: '/admin',
  folders: ['admin'],
  tags: ['internal'],
});

const adminComponents = adminFrontend.defineComponents().components((c) => ({
  AppsTable: c
    .component()
      .props({
        apps: appProjectionSchemas.ref.AppPartial.array(),
      })
      .uses({
        findApps: appRoutes.ref.findApps,
      })
      .tags(['table']),
  AppsFilters: c.component().props({
      query: appQuerySchemas.ref.AppListQuery,
    }),
  AppDetailsCard: c.component().props({
      app: appProjectionSchemas.ref.AppPublic,
    }),
}));

adminFrontend.defineScreens().screens((s) => ({
  AppsListScreen: s
      .screen('/apps')
      .title('Apps')
      .uses({
        findApps: appRoutes.ref.findApps,
      })
      .components({
        table: adminComponents.ref.AppsTable,
        filters: adminComponents.ref.AppsFilters,
      }),
  AppDetailScreen: s
      .screen('/apps/:id')
      .title('App Detail')
      .params(appRouteSchemas.ref.AppRouteParams)
      .query(appQuerySchemas.ref.AppListQuery)
      .uses({
        getAppById: appRoutes.ref.getAppById,
        updateApp: appRoutes.ref.updateApp,
      })
      .components({
        details: adminComponents.ref.AppDetailsCard,
      }),
}));

const customerFrontend = v1.defineFrontend({
  name: 'customer',
  title: 'Customer',
});

customerFrontend.defineComponents().components((c) => ({
  CustomerShell: c.component().title('Customer Shell'),
}));

const result = compileOpenApi(v1.contract);
assert.equal(result.success, true);

const document = result.document;
const codegen = document[CODEGEN_EXTENSION_KEY] as Record<string, any>;
assert.ok(codegen.frontends);
assert.ok(codegen.frontends.admin);
assert.ok(codegen.frontends.customer);
assert.equal(codegen.frontends.admin.name, 'admin');
assert.equal(codegen.frontends.admin.title, 'Admin');
assert.equal(codegen.frontends.admin.routePrefix, '/admin');
assert.deepEqual(codegen.frontends.admin.folders, ['admin']);
assert.deepEqual(codegen.frontends.admin.tags, ['internal']);

assert.deepEqual(codegen.frontends.admin.components.AppsTable.props, {
  $ref: '#/components/schemas/AdminAppsTableProps',
});
assert.deepEqual(codegen.frontends.admin.components.AppsTable.uses.findApps, {
  operationId: 'findApps',
  method: 'get',
  path: '/platform/apps',
  resource: {
    $ref: '#/x-codegen/resources/apps',
  },
});
assert.deepEqual(codegen.frontends.admin.components.AppsTable.schemas, [
  {
    $ref: '#/components/schemas/AppPartial',
  },
]);
assert.deepEqual(codegen.frontends.admin.components.AppsTable.tags, ['table']);

assert.deepEqual(codegen.frontends.admin.screens.AppsListScreen, {
  name: 'AppsListScreen',
  title: 'Apps',
  route: '/apps',
  fullRoute: '/admin/apps',
  components: {
    table: {
      $ref: '#/x-codegen/frontends/admin/components/AppsTable',
    },
    filters: {
      $ref: '#/x-codegen/frontends/admin/components/AppsFilters',
    },
  },
  uses: {
    findApps: {
      operationId: 'findApps',
      method: 'get',
      path: '/platform/apps',
      resource: {
        $ref: '#/x-codegen/resources/apps',
      },
    },
  },
});

assert.deepEqual(codegen.frontends.admin.screens.AppDetailScreen.params, {
  $ref: '#/components/schemas/AppRouteParams',
});
assert.deepEqual(codegen.frontends.admin.screens.AppDetailScreen.query, {
  $ref: '#/components/schemas/AppListQuery',
});

assert.deepEqual(document.components.schemas.AdminAppsTableProps, {
  type: 'object',
  properties: {
    apps: {
      type: 'array',
      items: {
        $ref: '#/components/schemas/AppPartial',
      },
    },
  },
  required: ['apps'],
  'x-codegen': {
    kind: 'dto',
    shared: true,
  },
});

const noFrontendVersion = defineVersionContract({
  info: {
    title: 'No Frontend API',
    version: '1.0.0',
  },
});
noFrontendVersion.defineResource({ name: 'users', route: '/users' });
const noFrontendResult = compileOpenApi(noFrontendVersion.contract);
assert.equal(noFrontendResult.success, true);
assert.equal((noFrontendResult.document[CODEGEN_EXTENSION_KEY] as Record<string, unknown> | undefined)?.frontends, undefined);

assert.throws(() => {
  v1.defineFrontend({ name: 'admin' });
}, /Duplicate frontend "admin"/);

assert.throws(() => {
  adminFrontend.defineComponents().components((c) => ({
    AppsTable: c.component(),
  }));
}, /Duplicate frontend component "AppsTable"/);

assert.throws(() => {
  adminFrontend.defineScreens().screens((s) => ({
    DuplicateAppsRoute: s.screen('/apps'),
  }));
}, /Duplicate frontend screen route "\/apps"/);

const invalid = defineVersionContract({
  info: {
    title: 'Invalid Frontend API',
    version: '1.0.0',
  },
});
const invalidResource = invalid.defineResource({ name: 'invalidApps', route: '/invalid/apps' });
const invalidResponses = invalidResource.defineSchemas({
  InvalidAppsResponse: {},
});
const invalidRoutes = invalidResource.defineRoutes({
  routes: {
    findInvalidApps: {
      method: HttpMethod.get,
      path: '/',
      response: invalidResponses.ref.InvalidAppsResponse,
    },
  },
});
const invalidAdmin = invalid.defineFrontend({ name: 'invalidAdmin' });
const invalidCustomer = invalid.defineFrontend({ name: 'invalidCustomer' });
const invalidCustomerComponents = invalidCustomer.defineComponents().components((c) => ({
  CustomerCard: c.component(),
}));
invalidAdmin.defineScreens().screens((s) => ({
  BadScreen: s
      .screen('/bad')
      .uses({
        findInvalidApps: invalidRoutes.ref.findInvalidApps,
      })
      .components({
        card: invalidCustomerComponents.ref.CustomerCard,
      }),
}));

assert.throws(() => {
  compileOpenApi(invalid.contract);
}, /references component "CustomerCard" from frontend "invalidCustomer"/);
