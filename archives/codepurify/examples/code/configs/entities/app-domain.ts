import * as cpy from 'codepurify';
import AppEntityConfig from './app';
import codepurifyTemplates from '../../../codepurify.templates';

export default class AppDomainEntityConfig implements cpy.IEntityConfig {
  base = null;
  workflows = [];
  key = 'app_domain';
  group_key = 'platform';
  options = { timestamps: true, audit: true };
  templates = [codepurifyTemplates];

  fields = cpy.defineFields({
    id: cpy.uuidField({
      query: cpy.query().defaultSelect().build(),
      mutation: cpy.mutation().systemOnly().generated().immutable().build(),
    }),
    appId: cpy.uuidField({
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().create('system').update(false).edit('system').persisted().immutable().build(),
    }),
    domain: cpy.stringField({
      length: 255,
      query: cpy.query().defaultSelect().sort().search().filter().build(),
      mutation: cpy.mutation().apiWritable().build(),
    }),

    isPrimary: cpy.booleanField({
      default: false,
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().apiWritable().build(),
      state: cpy.toggle(),
    }),
    isVerified: cpy.booleanField({
      default: false,
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().systemOnly().build(),
      state: cpy.toggle(),
    }),
    sslStatus: cpy.enumField(['none', 'pending', 'active', 'expired', 'error'] as const, {
      default: 'none',
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().systemOnly().build(),
    }),
    status: cpy.enumField(['active', 'inactive', 'suspended'] as const, {
      default: 'active',
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().apiWritable().build(),
    }),

    verifiedAt: cpy.stringField({ nullable: true, query: cpy.query().sort().build(), mutation: cpy.mutation().systemOnly().build() }),
    expiresAt: cpy.stringField({ nullable: true, query: cpy.query().filter().build(), mutation: cpy.mutation().apiWritable().build() }),
  });

  get relations(): Record<string, cpy.RelationConfigUnion> {
    return cpy.defineRelations({
      app: cpy.relationField(this, AppEntityConfig, {
        relation: {
          kind: 'many_to_one',
          local_field: () => this.fields.appId,
          remote_field: () => new AppEntityConfig().fields.name,
          on_delete: 'CASCADE',
        },
        query: { select: true },
      }),
    });
  }

  indexes = [
    { fields: [() => this.fields.appId] },
    { fields: [() => this.fields.domain], unique: true },
    { fields: [() => this.fields.isPrimary] },
    { fields: [() => this.fields.isVerified] },
    { fields: [() => this.fields.sslStatus] },
    { fields: [() => this.fields.status] },
    { fields: [() => this.fields.verifiedAt] },
    { fields: [() => this.fields.expiresAt] },
  ];

  checks = [
    {
      name: 'domain_not_empty',
      rule: cpy.field(() => this.fields.domain).notEmpty(),
    },
  ];

  transitions = [
    cpy.transition({
      field: () => this.fields.status,
      initial: this.fields.status.values.active,
      terminal: [],
      transitions: {
        [this.fields.status.values.active]: [this.fields.status.values.inactive, this.fields.status.values.suspended],
        [this.fields.status.values.inactive]: [this.fields.status.values.active, this.fields.status.values.suspended],
        [this.fields.status.values.suspended]: [this.fields.status.values.active, this.fields.status.values.inactive],
      },
    }),
  ];
}
