import assert from 'node:assert/strict';
import test from 'node:test';

import {
  DefaultAuthoringCompiler,
  defineCodepotConfig,
  defineVersionContract,
  z,
} from '../src/authoring/index';
import type { ResolvedSource } from '../src/contract/index';
import { Sha256Hash } from '../src/platform/index';

test('old-style contracts compile after import-only migration', async () => {
  const v1 = defineVersionContract({ info: { title: 'Compatibility', version: '1.0.0' } });
  const shared = v1.defineProperties('Shared', {
    id: z.string().regex(/^[a-f0-9]{24}$/i),
    name: z.string().min(1).max(100),
    status: z.enum(['active', 'disabled'] as const),
  });
  const schemas = v1.defineSchemas({
    User: {
      id: shared.ref.id,
      name: shared.ref.name,
      status: shared.ref.status,
    },
  });
  v1.defineSchemas({
    UserPreview: schemas.ref.User.pick({ id: true, name: true }),
  });
  const users = v1.defineResource({ name: 'users', route: '/v1/users', folders: ['platform'] });
  users.defineRoutes().routes((route) => ({
    listUsers: route.get('/').response(schemas.ref.User.array()),
    updateUser: route.patch('/:id')
      .body(schemas.ref.User.partial())
      .response(schemas.ref.User)
      .cache((cache) => cache.invalidate.on('listUsers')),
  }));

  const config = defineCodepotConfig({ contracts: [v1] });
  const source: ResolvedSource = {
    id: 'source:test',
    descriptor: { kind: 'memory', id: 'test' },
    root: '/project',
    entry: '/project/codepotx.config.ts',
    digest: 'source-digest',
    files: [],
  };
  const compiler = new DefaultAuthoringCompiler({ hash: new Sha256Hash() });
  const { artifact, diagnostics } = await compiler.compile({ config, source });

  assert.equal(diagnostics.filter((item) => item.severity === 'error').length, 0);
  assert.equal(artifact.header.kind, 'codepot.authoring');
  assert.deepEqual(artifact.operations.map((operation) => operation.operationId), ['listUsers', 'updateUser']);
  assert.deepEqual(artifact.operations[1]?.cacheInvalidates, ['listUsers']);
  assert.doesNotThrow(() => JSON.parse(JSON.stringify(artifact)));
});
