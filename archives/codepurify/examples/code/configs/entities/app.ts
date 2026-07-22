import * as cpy from 'codepurify';
import AppApiKeyEntityConfig from './app-api-key';
import AppDomainEntityConfig from './app-domain';
import UserEntityConfig from './user';
import codepurifyTemplates from '../../../codepurify.templates';

export default class AppEntityConfig implements cpy.IEntityConfig {
  base = null;
  workflows = [];
  key = 'app';
  group_key = 'platform';
  options = { timestamps: true, audit: true };
  templates = [codepurifyTemplates];

  fields = cpy.defineFields({
    name: cpy.stringField({
      length: 255,
      query: cpy.query().defaultSelect().sort().search().build(),
      mutation: cpy.mutation().apiWritable().build(),
    }),
    slug: cpy.stringField({
      length: 255,
      query: cpy.query().defaultSelect().sort().search().build(),
      mutation: cpy.mutation().apiCreateOnly().immutableAfterCreate().build(),
    }),
    description: cpy.stringField({ nullable: true, query: cpy.query().select().build(), mutation: cpy.mutation().apiWritable().build() }),

    isInternal: cpy.booleanField({
      default: false,
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().apiWritable().build(),
      state: cpy.toggle(),
    }),
    isActive: cpy.booleanField({
      default: true,
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().apiWritable().build(),
      state: cpy.toggle(),
    }),
    appType: cpy.enumField(['web', 'mobile', 'desktop'] as const, {
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().apiCreateOnly().immutableAfterCreate().build(),
    }),
    status: cpy.enumField(['active', 'suspended', 'archived'] as const, {
      default: 'active',
      query: cpy.query().sort().build(),
      mutation: cpy.mutation().systemOnly().build(),
    }),

    ownerId: cpy.foreignField(new UserEntityConfig(), {
      nullable: true,
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().create('system').update(false).edit('system').persisted().immutable().build(),
      business: { contextual: true, contextKey: 'owner' },
      system: { persisted: true },
    }),
  });

  relations: cpy.DefineRelation = {
    owner: cpy.relationField(this, UserEntityConfig, {
      relation: {
        kind: 'many_to_one',
        local_field: () => this.fields.ownerId,
        remote_field: () => new UserEntityConfig().fields.id,
        on_delete: 'CASCADE',
      },
      query: { select: true },
    }),

    apiKeys: cpy.relationField(this, AppApiKeyEntityConfig, {
      relation: {
        kind: 'one_to_many',
        remote_field: () => new AppApiKeyEntityConfig().fields.appId,
        cascade: true,
      },
      query: { select: true },
    }),

    domains: cpy.relationField(this, AppDomainEntityConfig, {
      relation: {
        kind: 'one_to_many',
        remote_field: () => new AppDomainEntityConfig().fields.appId,
        cascade: true,
      },
      query: { select: true },
    }),
  };

  indexes = [
    { fields: [() => this.fields.name] },
    { fields: [() => this.fields.slug], unique: true },
    { fields: [() => this.fields.appType, () => this.fields.status] },
    { fields: [() => this.fields.ownerId] },
  ];

  checks = [
    {
      name: 'name_not_empty',
      rule: cpy.field(() => this.fields.name).notEmpty(),
    },
    {
      name: 'slug_not_empty',
      rule: cpy.field(() => this.fields.slug).notEmpty(),
    },
  ];

  transitions = [
    cpy.transition({
      field: () => this.fields.status,
      initial: this.fields.status.values.active,
      terminal: [this.fields.status.values.archived],
      transitions: {
        [this.fields.status.values.active]: [this.fields.status.values.suspended, this.fields.status.values.archived],
        [this.fields.status.values.suspended]: [this.fields.status.values.active, this.fields.status.values.archived],
        [this.fields.status.values.archived]: [],
      },
    }),
  ];
}
