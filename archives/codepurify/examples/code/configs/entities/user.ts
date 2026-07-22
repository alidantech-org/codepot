import * as cpy from 'codepurify';
import AppEntityConfig from './app';
import codepurifyTemplates from '../../../codepurify.templates';

export default class UserEntityConfig implements cpy.IEntityConfig {
  base = null;
  workflows = [];
  key = 'user';
  group_key = 'platform';
  options = { timestamps: true, audit: true, softDelete: true };
  templates = [codepurifyTemplates];

  fields = cpy.defineFields({
    id: cpy.uuidField({
      query: cpy.query().defaultSelect().build(),
      mutation: cpy.mutation().systemOnly().generated().immutable().build(),
    }),
    email: cpy.stringField({
      length: 255,
      query: cpy.query().defaultSelect().sort().search().filter().build(),
      mutation: cpy.mutation().apiWritable().build(),
    }),
    username: cpy.stringField({
      length: 255,
      query: cpy.query().defaultSelect().sort().search().build(),
      mutation: cpy.mutation().apiWritable().build(),
    }),
    firstName: cpy.stringField({ length: 255, query: cpy.query().select().build(), mutation: cpy.mutation().apiWritable().build() }),
    lastName: cpy.stringField({ length: 255, query: cpy.query().select().build(), mutation: cpy.mutation().apiWritable().build() }),
    isActive: cpy.booleanField({
      default: true,
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().systemOnly().build(),
      state: cpy.toggle(),
    }),
    isEmailVerified: cpy.booleanField({
      default: false,
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().systemOnly().build(),
      state: cpy.toggle(),
    }),
    role: cpy.enumField(['admin', 'user', 'moderator'] as const, {
      default: 'user',
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().systemOnly().build(),
    }),
    status: cpy.enumField(['active', 'suspended', 'deleted'] as const, {
      default: 'active',
      query: cpy.query().filter().build(),
      mutation: cpy.mutation().systemOnly().build(),
    }),
  });

  relations: cpy.DefineRelation = {
    apps: cpy.relationField(this, AppEntityConfig, {
      relation: {
        kind: 'one_to_many',
        remote_field: () => new AppEntityConfig().fields.ownerId,
        cascade: true,
      },
      query: { select: true },
    }),
  };

  indexes = [
    { fields: [() => this.fields.email], unique: true },
    { fields: [() => this.fields.username], unique: true },
    { fields: [() => this.fields.isActive] },
    { fields: [() => this.fields.role] },
    { fields: [() => this.fields.status] },
  ];

  checks = [
    {
      name: 'email_not_empty',
      rule: cpy.field(() => this.fields.email).notEmpty(),
    },
    {
      name: 'username_not_empty',
      rule: cpy.field(() => this.fields.username).notEmpty(),
    },
    {
      name: 'email_format',
      rule: cpy.field(() => this.fields.email).regex('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'),
    },
  ];

  transitions = [
    cpy.enumTransition(this.fields.status.values, {
      initial: this.fields.status.values.active,
      terminal: [this.fields.status.values.deleted],
      transitions: {
        [this.fields.status.values.active]: [this.fields.status.values.suspended, this.fields.status.values.deleted],
        [this.fields.status.values.suspended]: [this.fields.status.values.active, this.fields.status.values.deleted],
        [this.fields.status.values.deleted]: [],
      },
    }),
  ];
}
