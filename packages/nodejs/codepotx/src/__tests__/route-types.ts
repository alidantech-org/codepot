import { z } from 'zod';
import { defineVersionContract } from '../index.js';

const v1 = defineVersionContract({
  info: {
    title: 'Route type tests',
    version: 'v1',
  },
});

const props = v1.defineProperties('Shared', {
  id: z.string(),
});

const resource = v1.defineResource({
  name: 'users',
  route: '/users',
});

const schemas = resource.defineSchemas({
  Params: {
    id: props.ref.id,
  },

  Ok: {
    id: props.ref.id,
  },
});

resource
  .defineRoutes()
  .params(schemas.ref.Params)
  .routes((r) => ({
    listUsers: r.get('/').response(schemas.ref.Ok),
  }));

resource.defineRoutes({
  params: schemas.ref.Params,
  routes: {
    getUser: {
      method: 'get',
      path: '/:id',
      response: schemas.ref.Ok,
    },
  },
});

if (false) {
  resource.defineRoutes().routes((r) => ({
    // @ts-expect-error operation names come from object keys only
    oldNameArg: r.get('/', 'listUsers'),
  }));

  resource.defineRoutes().routes((r) => ({
    // @ts-expect-error done() was removed
    oldDone: r.get('/').response(schemas.ref.Ok).done(),
  }));

  resource.defineRoutes().routes((r) => ({
    // @ts-expect-error endpoint-level params were removed
    oldParams: r.get('/:id').params({ id: props.ref.id }),
  }));

  resource.defineRoutes({
    routes: {
      badOperationId: {
        method: 'get',
        path: '/',
        // @ts-expect-error operationId is not allowed inside route objects
        operationId: 'otherName',
        response: schemas.ref.Ok,
      },
    },
  });
}
