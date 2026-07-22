import * as cpy from 'codepurify';
import AppEntityConfig from './app';
import codepurifyTemplates from '../../../codepurify.templates';

export default class AppApiKeyEntityConfig implements cpy.IEntityConfig {
  base = null;
  workflows = [];
  key = 'app_api_key';
  group_key = 'platform';

  fields = cpy.defineFields({
    id: cpy.uuidField({
      query: cpy.query().defaultSelect().build(),
      mutation: cpy.mutation().systemOnly().generated().immutable().build(),
    }),

    appId: cpy.uuidField({
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().create('system').update(false).edit('system').persisted().immutable().build(),
    }),

    name: cpy.stringField({
      length: 255,
      query: cpy.query().defaultSelect().sort().search().build(),
      mutation: cpy.mutation().apiWritable().build(),
    }),

    keyHash: cpy.secretStringField({
      length: 255,
      query: { select: false, filter: false },
      mutation: cpy.mutation().create('system').update('system').edit('system').persisted().build(),
    }),

    keyPrefix: cpy.stringField({
      length: 10,
      query: cpy.query().defaultSelect().build(),
      mutation: cpy.mutation().systemOnly().build(),
    }),

    isActive: cpy.booleanField({
      default: true,
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().apiWritable().build(),
      state: cpy.toggle(),
    }),
    expiresAt: cpy.stringField({ nullable: true, query: cpy.query().filter().build(), mutation: cpy.mutation().apiWritable().build() }),
    lastUsedAt: cpy.stringField({ nullable: true, query: cpy.query().sort().build(), mutation: cpy.mutation().systemOnly().build() }),

    permissions: cpy.enumField(['read', 'write', 'admin'] as const, {
      default: 'read',
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().apiWritable().build(),
    }),
    status: cpy.enumField(['active', 'expired', 'revoked'] as const, {
      default: 'active',
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().systemOnly().build(),
    }),
  });

  get relations(): Record<string, cpy.RelationConfigUnion> {
    return {
      app: cpy.relationField(this, AppEntityConfig, {
        relation: {
          kind: 'many_to_one',
          local_field: () => this.fields.appId,
          remote_field: () => new AppEntityConfig().fields.name,
          on_delete: 'CASCADE',
        },
        query: { select: true },
      }),
    };
  }

  indexes = [
    { fields: [() => this.fields.appId] },
    { fields: [() => this.fields.keyHash], unique: true },
    { fields: [() => this.fields.keyPrefix] },
    { fields: [() => this.fields.isActive] },
    { fields: [() => this.fields.expiresAt] },
    { fields: [() => this.fields.lastUsedAt] },
    { fields: [() => this.fields.status] },
  ];

  checks = [
    {
      name: 'name_not_empty',
      rule: cpy.field(() => this.fields.name).notEmpty(),
    },
    {
      name: 'key_prefix_not_empty',
      rule: cpy.field(() => this.fields.keyPrefix).notEmpty(),
    },
  ];

  transitions = [
    cpy.transition({
      field: () => this.fields.status,
      initial: this.fields.status.values.active,
      terminal: [this.fields.status.values.revoked],
      transitions: {
        [this.fields.status.values.active]: [this.fields.status.values.expired, this.fields.status.values.revoked],
        [this.fields.status.values.expired]: [this.fields.status.values.revoked],
        [this.fields.status.values.revoked]: [],
      },
    }),
  ];

  options = { timestamps: true, audit: true };
  templates = [codepurifyTemplates.pick(['types.context', 'constants', 'schema.entity'])];
}
