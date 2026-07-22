import { z } from 'zod';
import { sharedContract } from '../_global/shared.contract.js';
import { userContract } from '../users/user.resource.js';
import { v1 } from '../_global/version.contract.js';

const AuthNextStep = ['signup', 'login', 'verify-email', 'reset-password'] as const;

const auth = v1.defineResource({
  name: 'auth',
  route: 'v1/auth',
  folders: ['platform'],
  tags: ['platform', 'auth'],
  ui: {
    enabled: true,
    infer: false,
  },
});

const authFields = auth.defineProperties('AuthFields', {
  nextStep: z.enum(AuthNextStep),
  password: z.string().min(8).max(100),
  confirmPassword: z.string().min(8).max(100),
  newPassword: z.string().min(8).max(100),
  currentPassword: z.string().min(1),
  otp: z.string().length(6),
  idToken: z.string().min(1),
  token: z.string().min(1),
});

const authHooksRef = auth.defineHooks({
  setSessionCookies: {
    phase: 'afterSuccess',
    transport: {
      outbound: {
        cookies: true,
      },
    },
    description: 'Set access and refresh session cookies after successful authentication.',
  },

  auditFailedLogin: {
    phase: 'afterError',
    transport: {
      inbound: {
        ip: true,
        userAgent: true,
      },
    },
    description: 'Audit a failed login attempt.',
  },
}).ref;

const authBodies = auth.defineSchemas({
  ResolveEmailBody: {
    email: userContract.userProps.ref.email,
  },

  SignupBody: {
    email: userContract.userProps.ref.email,
    password: authFields.ref.password,
    confirmPassword: authFields.ref.confirmPassword,
    name: userContract.userProps.ref.name,
    phone: userContract.userProps.ref.phone.optional().nullable(),
    avatar: userContract.userProps.ref.avatar.optional().nullable(),
  },

  LoginBody: {
    email: userContract.userProps.ref.email,
    password: authFields.ref.password,
  },

  AdminLoginBody: {
    email: userContract.userProps.ref.email,
    password: authFields.ref.password,
  },

  GoogleSignInBody: {
    idToken: authFields.ref.idToken,
  },

  VerifyEmailBody: {
    email: userContract.userProps.ref.email,
    otp: authFields.ref.otp,
  },

  ResendVerificationEmailBody: {
    email: userContract.userProps.ref.email,
  },

  ForgotPasswordBody: {
    email: userContract.userProps.ref.email,
  },

  ResetPasswordBody: {
    email: userContract.userProps.ref.email,
    otp: authFields.ref.otp,
    newPassword: authFields.ref.newPassword,
    confirmPassword: authFields.ref.confirmPassword,
  },

  ChangePasswordBody: {
    currentPassword: authFields.ref.currentPassword,
    newPassword: authFields.ref.newPassword,
    confirmPassword: authFields.ref.confirmPassword,
  },
});

const authResponses = auth.defineSchemas({
  ResolveEmailOk: sharedContract.sharedSchemas.ref.ApiMessage.extendWith({
    email: userContract.userProps.ref.email,
    nextStep: authFields.ref.nextStep,
  }),

  SignupOk: sharedContract.sharedSchemas.ref.ApiMessage.extendWith({
    user: userContract.userPublicSchemas.ref.UserPublic,
    token: authFields.ref.token,
  }),

  AuthSessionOk: sharedContract.sharedSchemas.ref.ApiMessage.extendWith({
    user: userContract.userPublicSchemas.ref.UserPublic,
    token: authFields.ref.token,
  }),

  Conflict: sharedContract.sharedSchemas.ref.ApiMessage,
});

auth.defineRoutes().routes((r) => ({
  resolveEmail: r.post('/resolve-email').summary('Resolve email').body(authBodies.ref.ResolveEmailBody).response(authResponses.ref.ResolveEmailOk).ui('auth'),

  signup: r.post('/signup').summary('Sign up').body(authBodies.ref.SignupBody).on(201, authResponses.ref.SignupOk).on(409, authResponses.ref.Conflict).ui('auth'),

  login: r
    .post('/login')
    .summary('Login')
    .body(authBodies.ref.LoginBody)
    .on(200, authResponses.ref.AuthSessionOk)
    .on(401, sharedContract.sharedSchemas.ref.ApiMessage)
    .runtime({
      transport: {
        inbound: {
          ip: true,
          userAgent: true,
        },
      },
      hooks: {
        afterSuccess: authHooksRef.setSessionCookies,
        afterError: authHooksRef.auditFailedLogin,
      },
    })
    .ui('auth'),

  adminLogin: r
    .post('/admin/login')
    .summary('Admin login')
    .body(authBodies.ref.AdminLoginBody)
    .on(200, authResponses.ref.AuthSessionOk)
    .on(401, sharedContract.sharedSchemas.ref.ApiMessage)
    .on(403, sharedContract.sharedSchemas.ref.ApiMessage)
    .ui('auth'),

  googleSignIn: r.post('/google').summary('Google sign-in').body(authBodies.ref.GoogleSignInBody).on(200, authResponses.ref.AuthSessionOk).on(401, sharedContract.sharedSchemas.ref.ApiMessage).ui('auth'),

  verifyEmail: r.post('/verify-email').summary('Verify email').body(authBodies.ref.VerifyEmailBody).response(sharedContract.sharedSchemas.ref.ApiMessage).ui('auth'),

  resendVerificationEmail: r
    .post('/resend-verification-email')
    .summary('Resend verification email')
    .body(authBodies.ref.ResendVerificationEmailBody)
    .response(sharedContract.sharedSchemas.ref.ApiMessage)
    .ui('auth'),

  forgotPassword: r.post('/forgot-password').summary('Forgot password').body(authBodies.ref.ForgotPasswordBody).response(sharedContract.sharedSchemas.ref.ApiMessage).ui('auth'),

  resetPassword: r.post('/reset-password').summary('Reset password').body(authBodies.ref.ResetPasswordBody).response(sharedContract.sharedSchemas.ref.ApiMessage).ui('auth'),

  changePassword: r.put('/change-password').summary('Change password').body(authBodies.ref.ChangePasswordBody).response(sharedContract.sharedSchemas.ref.ApiMessage).ui('update'),
}));

export const authContract = {
  auth,
  authFields,
  authHooksRef,
  authBodies,
  authResponses,
};
