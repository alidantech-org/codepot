import { strict as assert } from 'node:assert';
import { z } from 'zod';
import { CODEGEN_EXTENSION_KEY, compileOpenApi, defineVersionContract } from '../index.js';

const v1 = defineVersionContract({
  info: {
    title: 'Runtime hooks',
    version: 'v1',
  },
});

const sharedProps = v1.defineProperties('Shared', {
  id: z.string(),
  message: z.string(),
});

const auth = v1.defineResource({
  name: 'auth',
  route: '/auth',
  folders: ['auth'],
});

const authHooks = auth.defineHooks({
  setSessionCookies: {
    phase: 'afterSuccess',
    transport: {
      outbound: {
        cookies: true,
      },
    },
    description: 'Set access and refresh session cookies after successful authentication.',
  },

  clearSessionCookies: {
    phase: 'afterSuccess',
    transport: {
      outbound: {
        cookies: true,
      },
    },
  },

  auditFailedLogin: {
    phase: 'afterError',
    transport: {
      inbound: {
        ip: true,
        userAgent: true,
      },
    },
  },

  prepareExportStream: {
    phase: 'beforeHandler',
    transport: {
      outbound: {
        stream: true,
      },
    },
  },

  writeExportStream: {
    phase: 'afterSuccess',
    transport: {
      outbound: {
        stream: true,
        bypassSerializer: true,
      },
    },
  },
});

const authSchemas = auth.defineSchemas({
  LoginBody: {
    id: sharedProps.ref.id,
  },

  AuthResponse: {
    message: sharedProps.ref.message,
  },
});

auth
  .defineRoutes()
  .routes((r) => ({
    login: r
      .post('/login')
      .body(authSchemas.ref.LoginBody)
      .response(authSchemas.ref.AuthResponse)
      .runtime({
        transport: {
          inbound: {
            correlationId: true,
          },
        },
        hooks: {
          afterSuccess: authHooks.ref.setSessionCookies,
          afterError: authHooks.ref.auditFailedLogin,
        },
      }),

    logout: r.post('/logout').response(authSchemas.ref.AuthResponse).runtime({
      hooks: {
        afterSuccess: [authHooks.ref.clearSessionCookies, authHooks.ref.setSessionCookies],
      },
    }),

    exportData: r.get('/export').response(authSchemas.ref.AuthResponse).runtime({
      hooks: {
        beforeHandler: authHooks.ref.prepareExportStream,
        afterSuccess: authHooks.ref.writeExportStream,
      },
    }),
  }));

auth.defineRoutes({
  routes: {
    loginObject: {
      method: 'post',
      path: '/login-object',
      body: authSchemas.ref.LoginBody,
      response: authSchemas.ref.AuthResponse,
      runtime: {
        transport: {
          outbound: {
            headers: true,
          },
        },
        hooks: {
          afterSuccess: authHooks.ref.setSessionCookies,
        },
      },
    },
  },
});

assert.equal(authHooks.ref.setSessionCookies.key, 'setSessionCookies');
assert.equal(authHooks.ref.setSessionCookies.phase, 'afterSuccess');
assert.deepEqual(authHooks.ref.setSessionCookies.owner, {
  resource: {
    name: 'auth',
    path: ['auth'],
  },
});

const result = compileOpenApi(v1.contract, { validate: false });
assert.equal(result.success, true);
if (!result.success) {
  throw new Error('Expected compileOpenApi to succeed.');
}

const document = result.document;

function operation(path: string, method: string): Record<string, unknown> {
  const pathItem = document.paths[path] as Record<string, unknown> | undefined;
  assert.ok(pathItem, `Expected path ${path}`);

  const op = pathItem[method] as Record<string, unknown> | undefined;
  assert.ok(op, `Expected ${method.toUpperCase()} ${path}`);
  return op;
}

function runtime(path: string, method: string): Record<string, unknown> {
  const meta = operation(path, method)[CODEGEN_EXTENSION_KEY] as Record<string, unknown> | undefined;
  assert.ok(meta?.runtime, `Expected x-codegen.runtime for ${method.toUpperCase()} ${path}`);
  return meta.runtime as Record<string, unknown>;
}

assert.deepEqual(runtime('/auth/login', 'post').transport, {
  inbound: {
    correlationId: true,
    ip: true,
    userAgent: true,
  },
  outbound: {
    cookies: true,
  },
});

assert.deepEqual((runtime('/auth/login', 'post').hooks as Record<string, unknown>).afterSuccess, [
  {
    $ref: '#/x-codegen/resources/auth/hooks/setSessionCookies',
  },
]);
assert.deepEqual((runtime('/auth/login', 'post').hooks as Record<string, unknown>).afterError, [
  {
    $ref: '#/x-codegen/resources/auth/hooks/auditFailedLogin',
  },
]);
assert.equal(JSON.stringify(runtime('/auth/login', 'post').hooks).includes('"key"'), false);
assert.equal(JSON.stringify(runtime('/auth/login', 'post').hooks).includes('"owner"'), false);
assert.equal(JSON.stringify(runtime('/auth/login', 'post').hooks).includes('transport'), false);
assert.equal(JSON.stringify(runtime('/auth/login', 'post').hooks).includes('description'), false);

assert.deepEqual(runtime('/auth/logout', 'post').transport, {
  outbound: {
    cookies: true,
  },
});
assert.equal(((runtime('/auth/logout', 'post').hooks as Record<string, unknown>).afterSuccess as unknown[]).length, 2);

assert.deepEqual(runtime('/auth/export', 'get').transport, {
  outbound: {
    stream: true,
    bypassSerializer: true,
  },
});

assert.deepEqual(runtime('/auth/login-object', 'post').transport, {
  outbound: {
    headers: true,
    cookies: true,
  },
});

const documentCodegen = document[CODEGEN_EXTENSION_KEY] as Record<string, unknown>;
assert.deepEqual(((documentCodegen.resources as Record<string, Record<string, unknown>>).auth.hooks as Record<string, unknown>).setSessionCookies, {
  phase: 'afterSuccess',
  transport: {
    outbound: {
      cookies: true,
    },
  },
  description: 'Set access and refresh session cookies after successful authentication.',
});

const runtimePayload = [
  runtime('/auth/login', 'post'),
  runtime('/auth/logout', 'post'),
  runtime('/auth/export', 'get'),
  runtime('/auth/login-object', 'post'),
  (documentCodegen.resources as Record<string, unknown>).auth,
];

for (const forbidden of ['req', 'res', 'request', 'response', 'express', 'nest', 'fastify', 'middleware', 'interceptor']) {
  assert.equal(hasForbiddenRuntimeToken(runtimePayload, forbidden), false, `Runtime metadata should not include "${forbidden}".`);
}

assert.throws(() =>
  compileOpenApi(
    v1.defineResource({ name: 'bad-runtime', route: '/bad-runtime' })
      .defineRoutes()
      .routes((r) => ({
        badHookPhase: r.get('/').runtime({
          hooks: {
            beforeHandler: authHooks.ref.setSessionCookies as never,
          },
        }),
      })) && v1.contract,
    { validate: false },
  ),
);

if (false) {
  auth.defineRoutes().routes((r) => ({
    badRawRuntime: r.get('/').runtime({
      // @ts-expect-error old raw runtime shape is not supported
      raw: ['request', 'response'],
    }),

    badHookString: r.get('/').runtime({
      hooks: {
        // @ts-expect-error raw hook strings are not supported
        afterSuccess: 'auth.setSessionCookies',
      },
    }),

    badHookPhase: r.get('/').runtime({
      hooks: {
        // @ts-expect-error hook phase must match placement
        beforeHandler: authHooks.ref.setSessionCookies,
      },
    }),
  }));
}

function hasForbiddenRuntimeToken(value: unknown, token: string): boolean {
  if (typeof value === 'string') return value.toLowerCase() === token;

  if (Array.isArray(value)) {
    return value.some((item) => hasForbiddenRuntimeToken(item, token));
  }

  if (value && typeof value === 'object') {
    return Object.entries(value).some(([key, child]) => key.toLowerCase() === token || hasForbiddenRuntimeToken(child, token));
  }

  return false;
}
