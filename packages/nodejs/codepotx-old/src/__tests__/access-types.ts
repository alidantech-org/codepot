import { z } from 'zod';
import { defineVersionContract } from '../index.js';

const USER_ROLES = ['user', 'admin', 'super_admin'] as const;

const v1 = defineVersionContract({
  info: {
    title: 'Access type tests',
    version: 'v1',
  },
});

const users = v1.defineResource({
  name: 'users',
  route: '/users',
});

const userProps = users.defineProperties('User', {
  role: z.enum(USER_ROLES),
  username: z.string(),
});

userProps.ref.role.allow({
  admin: true,
  super_admin: true,
});

userProps.ref.role.allow({
  // @ts-expect-error invalid role key
  superadmin: true,
});

// @ts-expect-error allow is only exposed for string-literal-like property refs
userProps.ref.username.allow({
  admin: true,
});
