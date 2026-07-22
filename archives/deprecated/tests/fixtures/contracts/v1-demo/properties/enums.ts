import { property } from '@/index';

import { properties } from '../version';


// ============================================================================
// GLOBAL ENUMS
// ============================================================================

export const enums = properties.enums({
  // User-related enums
  UserRole: property.enum({
    owner: { value: 'owner', label: 'Owner' },
    admin: { value: 'admin', label: 'Admin' },
    member: { value: 'member', label: 'Member' },
  }),

  UserStatus: property.enum({
    active: { value: 'active', label: 'Active' },
    suspended: { value: 'suspended', label: 'Suspended' },
  }),

  // Tenant-related enums
  TenantPlan: property.enum({
    free: { value: 'free', label: 'Free' },
    starter: { value: 'starter', label: 'Starter' },
    professional: { value: 'professional', label: 'Professional' },
    enterprise: { value: 'enterprise', label: 'Enterprise' },
  }),

  // Project-related enums
  ProjectStatus: property.enum({
    planning: { value: 'planning', label: 'Planning' },
    active: { value: 'active', label: 'Active' },
    on_hold: { value: 'on_hold', label: 'On Hold' },
    completed: { value: 'completed', label: 'Completed' },
    archived: { value: 'archived', label: 'Archived' },
  }),

  // Task-related enums
  TaskStatus: property.enum({
    backlog: { value: 'backlog', label: 'Backlog' },
    todo: { value: 'todo', label: 'To Do' },
    in_progress: { value: 'in_progress', label: 'In Progress' },
    review: { value: 'review', label: 'Review' },
    done: { value: 'done', label: 'Done' },
    cancelled: { value: 'cancelled', label: 'Cancelled' },
  }),

  TaskPriority: property.enum({
    low: { value: 'low', label: 'Low' },
    medium: { value: 'medium', label: 'Medium' },
    high: { value: 'high', label: 'High' },
    urgent: { value: 'urgent', label: 'Urgent' },
  }),

  // Invoice-related enums
  InvoiceStatus: property.enum({
    draft: { value: 'draft', label: 'Draft' },
    sent: { value: 'sent', label: 'Sent' },
    paid: { value: 'paid', label: 'Paid' },
    overdue: { value: 'overdue', label: 'Overdue' },
    cancelled: { value: 'cancelled', label: 'Cancelled' },
  }),

  PaymentStatus: property.enum({
    pending: { value: 'pending', label: 'Pending' },
    processing: { value: 'processing', label: 'Processing' },
    completed: { value: 'completed', label: 'Completed' },
    failed: { value: 'failed', label: 'Failed' },
    refunded: { value: 'refunded', label: 'Refunded' },
  }),

  // Webhook-related enums
  WebhookEventType: property.enum({
    user_created: { value: 'user.created', label: 'User Created' },
    user_updated: { value: 'user.updated', label: 'User Updated' },
    user_deleted: { value: 'user.deleted', label: 'User Deleted' },
    project_created: { value: 'project.created', label: 'Project Created' },
    project_updated: { value: 'project.updated', label: 'Project Updated' },
    task_created: { value: 'task.created', label: 'Task Created' },
    task_updated: { value: 'task.updated', label: 'Task Updated' },
    invoice_paid: { value: 'invoice.paid', label: 'Invoice Paid' },
  }),

  // Audit-related enums
  AuditAction: property.enum({
    create: { value: 'create', label: 'Create' },
    read: { value: 'read', label: 'Read' },
    update: { value: 'update', label: 'Update' },
    delete: { value: 'delete', label: 'Delete' },
    login: { value: 'login', label: 'Login' },
    logout: { value: 'logout', label: 'Logout' },
  }),

  // Notification-related enums
  NotificationChannel: property.enum({
    email: { value: 'email', label: 'Email' },
    sms: { value: 'sms', label: 'SMS' },
    push: { value: 'push', label: 'Push' },
    in_app: { value: 'in_app', label: 'In App' },
  }),

  // API key-related enums
  ApiKeyStatus: property.enum({
    active: { value: 'active', label: 'Active' },
    revoked: { value: 'revoked', label: 'Revoked' },
    expired: { value: 'expired', label: 'Expired' },
  }),

  // Post-related enums (legacy)
  PostStatus: property.enum({
    draft: { value: 'draft', label: 'Draft' },
    published: { value: 'published', label: 'Published' },
    archived: { value: 'archived', label: 'Archived' },
  }),
});