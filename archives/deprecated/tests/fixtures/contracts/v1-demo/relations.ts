import {
  apiKey,
  auditLog,
  invoice,
  invoiceLine,
  notification,
  payment,
  post,
  postTag,
  profile,
  project,
  tag,
  task,
  taskAttachment,
  taskComment,
  taskTag,
  tenant,
  user,
  webhookDelivery,
  webhookEndpoint,
} from './entities';

// ============================================================================
// RELATION LINKING
// ============================================================================

user.relations({
  tenant: (r) => r.belongsTo(tenant),

  profile: (r) => r.hasOne(profile).inverse(profile.ref.fields.user),

  posts: (r) => r.hasMany(post).inverse(post.ref.fields.author),
});

profile.relations({
  user: (r) => r.belongsTo(user).inverse(user.ref.fields.profile),

  tenantSnapshot: (r) => r.hasOne(tenant),
});

post.relations({
  author: (r) => r.belongsTo(user).inverse(user.ref.fields.posts),

  tags: (r) =>
    r
      .manyToMany(tag)
      .through(postTag, {
        from: postTag.ref.fields.post,
        to: postTag.ref.fields.tag,
      })
      .inverse(tag.ref.fields.posts),

  relatedProfiles: (r) => r.hasMany(profile),
});

tag.relations({
  posts: (r) =>
    r
      .manyToMany(post)
      .through(postTag, {
        from: postTag.ref.fields.tag,
        to: postTag.ref.fields.post,
      })
      .inverse(post.ref.fields.tags),

  tasks: (r) =>
    r
      .manyToMany(task)
      .through(taskTag, {
        from: taskTag.ref.fields.tag,
        to: taskTag.ref.fields.task,
      })
      .inverse(task.ref.fields.tags),
});

postTag.relations({
  post: (r) => r.belongsTo(post),

  tag: (r) => r.belongsTo(tag),
});

project.relations({
  tenant: (r) => r.belongsTo(tenant),

  owner: (r) => r.belongsTo(user),

  tasks: (r) => r.hasMany(task).inverse(task.ref.fields.project),
});

task.relations({
  project: (r) => r.belongsTo(project).inverse(project.ref.fields.tasks),

  assignee: (r) => r.belongsTo(user),

  comments: (r) => r.hasMany(taskComment).inverse(taskComment.ref.fields.task),

  attachments: (r) => r.hasMany(taskAttachment).inverse(taskAttachment.ref.fields.task),

  tags: (r) =>
    r
      .manyToMany(tag)
      .through(taskTag, {
        from: taskTag.ref.fields.task,
        to: taskTag.ref.fields.tag,
      })
      .inverse(tag.ref.fields.tasks),
});

taskTag.relations({
  task: (r) => r.belongsTo(task),

  tag: (r) => r.belongsTo(tag),
});

taskComment.relations({
  task: (r) => r.belongsTo(task).inverse(task.ref.fields.comments),

  author: (r) => r.belongsTo(user),
});

taskAttachment.relations({
  task: (r) => r.belongsTo(task).inverse(task.ref.fields.attachments),

  uploadedBy: (r) => r.belongsTo(user),
});

invoice.relations({
  tenant: (r) => r.belongsTo(tenant),

  lines: (r) => r.hasMany(invoiceLine).inverse(invoiceLine.ref.fields.invoice),

  payments: (r) => r.hasMany(payment).inverse(payment.ref.fields.invoice),
});

invoiceLine.relations({
  invoice: (r) => r.belongsTo(invoice).inverse(invoice.ref.fields.lines),
});

payment.relations({
  invoice: (r) => r.belongsTo(invoice).inverse(invoice.ref.fields.payments),
});

apiKey.relations({
  user: (r) => r.belongsTo(user),
});

webhookEndpoint.relations({
  tenant: (r) => r.belongsTo(tenant),

  deliveries: (r) => r.hasMany(webhookDelivery).inverse(webhookDelivery.ref.fields.endpoint),
});

webhookDelivery.relations({
  endpoint: (r) => r.belongsTo(webhookEndpoint).inverse(webhookEndpoint.ref.fields.deliveries),
});

auditLog.relations({
  user: (r) => r.belongsTo(user),
});

notification.relations({
  user: (r) => r.belongsTo(user),
});
