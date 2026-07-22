import { strict as assert } from 'node:assert';
import { z } from 'zod';
import { ContentType, HttpMethod, compileOpenApi, defineVersionContract } from '../index.js';

const v1 = defineVersionContract({
  info: {
    title: 'Projection API',
    version: 'v1',
  },
});

const sharedProps = v1.defineProperties('Shared', {
  id: z.string(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  message: z.string(),
});

const sharedSchemas = v1.defineSchemas({
  PublicBaseEntity: {
    id: sharedProps.ref.id,
    createdAt: sharedProps.ref.createdAt,
    updatedAt: sharedProps.ref.updatedAt,
  },

  ApiMessage: {
    message: sharedProps.ref.message,
  },
});

const uploads = v1.defineResource({
  name: 'uploads',
  route: '/uploads',
});

const uploadProps = uploads.defineProperties('Upload', {
  originalName: z.string(),
  secureUrl: z.string().url(),
  mimeType: z.string(),
  status: z.enum(['pending', 'ready']),
  storage: z.string(),
  password: z.string(),
  file: z.string(),
});

const uploadBodySchemas = uploads.defineSchemas({
  UploadFileBody: {
    file: uploadProps.ref.file,
  },
});

const uploadPublicSchemas = uploads.defineSchemas({
  UploadPublic: sharedSchemas.ref.PublicBaseEntity.extendWith({
    originalName: uploadProps.ref.originalName,
    secureUrl: uploadProps.ref.secureUrl,
    mimeType: uploadProps.ref.mimeType,
    status: uploadProps.ref.status,
    storage: uploadProps.ref.storage,
    password: uploadProps.ref.password,
  }),
});

const uploadMutableSchemas = uploads.defineSchemas({
  UploadMutable: {
    originalName: uploadProps.ref.originalName,
    secureUrl: uploadProps.ref.secureUrl,
    mimeType: uploadProps.ref.mimeType,
    status: uploadProps.ref.status,
  },
});

const uploadProjectionSchemas = uploads.defineSchemas({
  UploadPartial: uploadPublicSchemas.ref.UploadPublic.partial(),
  UploadPreview: uploadPublicSchemas.ref.UploadPublic.pick({
    id: true,
    originalName: true,
    secureUrl: true,
    mimeType: true,
    status: true,
  }),
  UploadSafe: uploadPublicSchemas.ref.UploadPublic.omit({
    password: true,
    storage: true,
  }),
});

const uploadNestedProjectionSchemas = uploads.defineSchemas({
  UploadPreviewPartial: uploadProjectionSchemas.ref.UploadPreview.partial(),
  UploadPreviewWithoutStatus: uploadProjectionSchemas.ref.UploadPreview.omit({
    status: true,
  }),
  UploadTinyPreview: uploadProjectionSchemas.ref.UploadPreview.pick({
    id: true,
    secureUrl: true,
  }),
  UploadFilterable: uploadPublicSchemas.ref.UploadPublic.pick({
    id: true,
    originalName: true,
    secureUrl: true,
    mimeType: true,
    status: true,
    createdAt: true,
    updatedAt: true,
  }).partial(),
  UploadSafeDraft: uploadPublicSchemas.ref.UploadPublic.omit({
    password: true,
    storage: true,
  }).partial(),
  UploadPublicWithoutSecretsDraft: uploadPublicSchemas.ref.UploadPublic.partial().omit({
    password: true,
    storage: true,
  }),
});

const uploadMutableProjectionSchemas = uploads.defineSchemas({
  UpdateUploadBody: uploadMutableSchemas.ref.UploadMutable.partial(),
});

const uploadMutableNestedProjectionSchemas = uploads.defineSchemas({
  UpdateUploadNameOnly: uploadMutableProjectionSchemas.ref.UpdateUploadBody.pick({
    originalName: true,
  }),
  UpdateUploadWithoutStatus: uploadMutableProjectionSchemas.ref.UpdateUploadBody.omit({
    status: true,
  }),
});

function assertProjectionTypes(): void {
  // @ts-expect-error projection maps only accept known schema fields
  uploadPublicSchemas.ref.UploadPublic.pick({ wrongField: true });
  // @ts-expect-error projection maps only accept true values
  uploadPublicSchemas.ref.UploadPublic.pick({ id: false });
  // @ts-expect-error projections are definitions, not schema field values
  uploads.defineSchemas({ BadInlineProjection: { upload: uploadPublicSchemas.ref.UploadPublic.pick({ id: true }) } });
  // @ts-expect-error projection helpers do not accept names
  uploadPublicSchemas.ref.UploadPublic.partial('UploadPartial');
  // @ts-expect-error projected refs only expose their narrowed field set
  uploadProjectionSchemas.ref.UploadPreview.pick({ storage: true });
  // @ts-expect-error chained projections keep narrowing their field set
  uploadPublicSchemas.ref.UploadPublic.pick({ id: true }).partial().pick({ storage: true });
  // @ts-expect-error partial does not reintroduce fields omitted earlier in the chain
  uploadPublicSchemas.ref.UploadPublic.omit({ storage: true }).partial().pick({ storage: true });
}

void assertProjectionTypes;

assert.throws(
  () =>
    uploads.defineSchemas({
      UploadPreview: uploadPublicSchemas.ref.UploadPublic.pick({
        id: true,
        status: true,
      }),
    }),
  /Duplicate schema component "UploadPreview"/,
);
assert.throws(
  () => uploads.defineSchemas({ BadRuntimeField: uploadPublicSchemas.ref.UploadPublic.pick(JSON.parse('{"notAField":true}')) }),
  /unknown field "notAField"/,
);
assert.throws(
  () => uploadPublicSchemas.ref.UploadPublic.pick(JSON.parse('{"id":false}')),
  /must be true\. Use only/,
);
assert.throws(
  () => {
    const invalid = defineVersionContract({ info: { title: 'Invalid inline projection', version: 'v1' } });
    const invalidProps = invalid.defineProperties('Invalid', { id: z.string(), message: z.string() });
    const invalidBase = invalid.defineSchemas({
      ApiMessage: { message: invalidProps.ref.message },
      InvalidPublic: { id: invalidProps.ref.id },
    });

    invalid.defineSchemas({
      BadInlineProjectionRuntime: {
        upload: invalidBase.ref.InvalidPublic.pick({ id: true }),
      } as never,
    });

    compileOpenApi(invalid.contract, { validate: false });
  },
  /Schema projections must be declared as top-level defineSchemas/,
);

const uploadResponseSchemas = uploads.defineSchemas({
  UploadOk: sharedSchemas.ref.ApiMessage.extendWith({
    upload: uploadProjectionSchemas.ref.UploadPartial,
  }),

  UploadPreviewOk: sharedSchemas.ref.ApiMessage.extendWith({
    upload: uploadProjectionSchemas.ref.UploadPreview.optional(),
  }),

  UploadsOk: sharedSchemas.ref.ApiMessage.extendWith({
    uploads: uploadProjectionSchemas.ref.UploadSafe.array(),
  }),

  UploadTinyPreviewOk: sharedSchemas.ref.ApiMessage.extendWith({
    upload: uploadNestedProjectionSchemas.ref.UploadTinyPreview,
  }),

  NullableUploadOk: sharedSchemas.ref.ApiMessage.extendWith({
    upload: uploadPublicSchemas.ref.UploadPublic.nullable(),
  }),
});

uploads.defineRoutes({
  routes: {
    createUpload: {
      method: HttpMethod.post,
      path: '/',
      summary: 'Upload file',
      body: {
        schema: uploadBodySchemas.ref.UploadFileBody,
        contentType: ContentType.multipartFormData,
        required: true,
      },
      responses: {
        201: uploadResponseSchemas.ref.UploadOk,
      },
    },
  },
});

const result = compileOpenApi(v1.contract, { validate: false });
assert.equal(result.success, true);

const schemas = result.document.components.schemas as Record<string, Record<string, unknown>>;
assert.deepEqual(Object.keys((schemas.UploadPreview.properties as Record<string, unknown>) ?? {}), [
  'id',
  'originalName',
  'secureUrl',
  'mimeType',
  'status',
]);
assert.ok(!('password' in ((schemas.UploadSafe.properties as Record<string, unknown>) ?? {})));
assert.ok(!('storage' in ((schemas.UploadSafe.properties as Record<string, unknown>) ?? {})));
assert.equal(schemas.UploadPartial.required, undefined);
assert.deepEqual((schemas.UploadPreview.properties as Record<string, unknown>).id, { $ref: '#/components/schemas/SharedId' });
assert.deepEqual((schemas.UploadPreview['x-codegen'] as { projection?: unknown }).projection, {
  source: 'UploadPublic',
  rootSource: 'UploadPublic',
  mode: 'pick',
  fields: ['id', 'originalName', 'secureUrl', 'mimeType', 'status'],
});
assert.deepEqual(Object.keys((schemas.UploadPreviewPartial.properties as Record<string, unknown>) ?? {}), [
  'id',
  'originalName',
  'secureUrl',
  'mimeType',
  'status',
]);
assert.equal(schemas.UploadPreviewPartial.required, undefined);
assert.deepEqual(Object.keys((schemas.UploadPreviewWithoutStatus.properties as Record<string, unknown>) ?? {}), [
  'id',
  'originalName',
  'secureUrl',
  'mimeType',
]);
assert.deepEqual(Object.keys((schemas.UploadTinyPreview.properties as Record<string, unknown>) ?? {}), ['id', 'secureUrl']);
assert.deepEqual((schemas.UploadTinyPreview['x-codegen'] as { projection?: unknown }).projection, {
  source: 'UploadPreview',
  rootSource: 'UploadPublic',
  mode: 'pick',
  fields: ['id', 'secureUrl'],
});
assert.equal(schemas.UploadFilterable.required, undefined);
assert.deepEqual(Object.keys((schemas.UploadFilterable.properties as Record<string, unknown>) ?? {}), [
  'id',
  'originalName',
  'secureUrl',
  'mimeType',
  'status',
  'createdAt',
  'updatedAt',
]);
assert.deepEqual((schemas.UploadFilterable['x-codegen'] as { projection?: unknown }).projection, {
  source: 'UploadPublic',
  rootSource: 'UploadPublic',
  mode: 'partial',
  steps: [
    {
      mode: 'pick',
      fields: ['id', 'originalName', 'secureUrl', 'mimeType', 'status', 'createdAt', 'updatedAt'],
    },
    {
      mode: 'partial',
    },
  ],
});
assert.equal(schemas.UploadSafeDraft.required, undefined);
assert.deepEqual(Object.keys((schemas.UploadSafeDraft.properties as Record<string, unknown>) ?? {}), [
  'id',
  'createdAt',
  'updatedAt',
  'originalName',
  'secureUrl',
  'mimeType',
  'status',
]);
assert.equal(schemas.UploadPublicWithoutSecretsDraft.required, undefined);
assert.deepEqual(Object.keys((schemas.UploadPublicWithoutSecretsDraft.properties as Record<string, unknown>) ?? {}), [
  'id',
  'createdAt',
  'updatedAt',
  'originalName',
  'secureUrl',
  'mimeType',
  'status',
]);
assert.equal(schemas.UpdateUploadBody.required, undefined);
assert.equal(schemas.UpdateUploadNameOnly.required, undefined);
assert.deepEqual(Object.keys((schemas.UpdateUploadNameOnly.properties as Record<string, unknown>) ?? {}), ['originalName']);
assert.deepEqual((schemas.UpdateUploadNameOnly['x-codegen'] as { projection?: unknown }).projection, {
  source: 'UpdateUploadBody',
  rootSource: 'UploadMutable',
  mode: 'pick',
  fields: ['originalName'],
});
assert.equal(schemas.UpdateUploadWithoutStatus.required, undefined);
assert.deepEqual(Object.keys((schemas.UpdateUploadWithoutStatus.properties as Record<string, unknown>) ?? {}), [
  'originalName',
  'secureUrl',
  'mimeType',
]);
assert.deepEqual((schemas.UpdateUploadWithoutStatus['x-codegen'] as { projection?: unknown }).projection, {
  source: 'UpdateUploadBody',
  rootSource: 'UploadMutable',
  mode: 'omit',
  fields: ['status'],
});

const uploadPreviewOkAllOf = schemas.UploadPreviewOk.allOf as readonly { properties?: Record<string, unknown>; required?: string[] }[];
const uploadPreviewOkExtension = uploadPreviewOkAllOf[1];
assert.ok(!uploadPreviewOkExtension.required?.includes('upload'));
assert.deepEqual(uploadPreviewOkExtension.properties?.upload, { $ref: '#/components/schemas/UploadPreview' });

const uploadsOkAllOf = schemas.UploadsOk.allOf as readonly { properties?: Record<string, unknown> }[];
assert.deepEqual(uploadsOkAllOf[1].properties?.uploads, {
  type: 'array',
  items: { $ref: '#/components/schemas/UploadSafe' },
});

const nullableUploadOkAllOf = schemas.NullableUploadOk.allOf as readonly { properties?: Record<string, unknown> }[];
assert.deepEqual(nullableUploadOkAllOf[1].properties?.upload, {
  anyOf: [{ $ref: '#/components/schemas/UploadPublic' }, { type: 'null' }],
});

const createUploadPath = Object.values(result.document.paths).find((pathItem) => {
  return !!pathItem.post && pathItem.post.summary === 'Upload file';
});
const createUpload = createUploadPath?.post as { requestBody?: { content?: Record<string, unknown> } } | undefined;
assert.ok(createUpload);
const multipartRequestBody = Object.values(result.document.components.requestBodies ?? {}).find((requestBody) => {
  return !!(requestBody as { content?: Record<string, unknown> }).content?.[ContentType.multipartFormData];
});
assert.ok(multipartRequestBody);
