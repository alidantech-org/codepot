import { HttpMethod } from 'codepot-openapi';
import { z } from 'zod';
import { sharedContract } from '../_global/shared.contract.js';
import { v1 } from '../_global/version.contract.js';

const ThemeMode = ['system', 'light', 'dark'] as const;
const DistanceUnit = ['km', 'mi'] as const;
const LanguageCode = ['en', 'sw', 'fr'] as const;

const userSettings = v1.defineResource({
  name: 'user-settings',
  route: 'v1/users/:userId/settings',
  folders: ['platform'],
  tags: ['platform', 'users', 'settings'],
  ui: {
    enabled: true,
    infer: false,
  },
});

const settingsProps = userSettings.defineProperties('UserSettings', {
  id: z.string().regex(/^[a-f\d]{24}$/i),
  userId: z.string().regex(/^[a-f\d]{24}$/i),
  pushEnabled: z.boolean(),
  emailEnabled: z.boolean(),
  smsEnabled: z.boolean(),
  marketingEnabled: z.boolean(),
  tripUpdatesEnabled: z.boolean(),
  emergencyAlertsEnabled: z.boolean(),
  profileVisible: z.boolean(),
  shareLiveLocation: z.boolean(),
  theme: z.enum(ThemeMode),
  distanceUnit: z.enum(DistanceUnit),
  language: z.enum(LanguageCode),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

const settingsCompositeSchemas = userSettings.defineSchemas({
  NotificationSettings: {
    pushEnabled: settingsProps.ref.pushEnabled,
    emailEnabled: settingsProps.ref.emailEnabled,
    smsEnabled: settingsProps.ref.smsEnabled,
    marketingEnabled: settingsProps.ref.marketingEnabled,
    tripUpdatesEnabled: settingsProps.ref.tripUpdatesEnabled,
    emergencyAlertsEnabled: settingsProps.ref.emergencyAlertsEnabled,
  },

  PrivacySettings: {
    profileVisible: settingsProps.ref.profileVisible,
    shareLiveLocation: settingsProps.ref.shareLiveLocation,
  },

  DisplaySettings: {
    theme: settingsProps.ref.theme,
    distanceUnit: settingsProps.ref.distanceUnit,
    language: settingsProps.ref.language,
  },
});

const settingsPublicSchemas = userSettings.defineSchemas({
  UserSettingsPublic: sharedContract.publicBaseEntity.extendWith({
    userId: settingsProps.ref.userId,
    notifications: settingsCompositeSchemas.ref.NotificationSettings,
    privacy: settingsCompositeSchemas.ref.PrivacySettings,
    display: settingsCompositeSchemas.ref.DisplaySettings,
  }),
});

const settingsUpdateBodySchemas = userSettings.defineSchemas({
  UpdateNotificationSettingsBody: {
    pushEnabled: settingsProps.ref.pushEnabled.optional(),
    emailEnabled: settingsProps.ref.emailEnabled.optional(),
    smsEnabled: settingsProps.ref.smsEnabled.optional(),
    marketingEnabled: settingsProps.ref.marketingEnabled.optional(),
    tripUpdatesEnabled: settingsProps.ref.tripUpdatesEnabled.optional(),
    emergencyAlertsEnabled: settingsProps.ref.emergencyAlertsEnabled.optional(),
  },

  UpdatePrivacySettingsBody: {
    profileVisible: settingsProps.ref.profileVisible.optional(),
    shareLiveLocation: settingsProps.ref.shareLiveLocation.optional(),
  },

  UpdateDisplaySettingsBody: {
    theme: settingsProps.ref.theme.optional(),
    distanceUnit: settingsProps.ref.distanceUnit.optional(),
    language: settingsProps.ref.language.optional(),
  },
});

const settingsSchemas = userSettings.defineSchemas({
  UserSettingsRouteParams: {
    userId: settingsProps.ref.userId,
  },

  UserSettingsOk: sharedContract.sharedSchemas.ref.ApiMessage.extendWith({
    settings: settingsPublicSchemas.ref.UserSettingsPublic,
  }),

  UpdateUserSettingsBody: {
    notifications: settingsUpdateBodySchemas.ref.UpdateNotificationSettingsBody.optional(),
    privacy: settingsUpdateBodySchemas.ref.UpdatePrivacySettingsBody.optional(),
    display: settingsUpdateBodySchemas.ref.UpdateDisplaySettingsBody.optional(),
  },
});

userSettings.defineRoutes({
  params: settingsSchemas.ref.UserSettingsRouteParams,

  routes: {
    getUserSettings: {
      method: HttpMethod.get,
      path: '/',
      summary: 'Get user settings',
      response: settingsSchemas.ref.UserSettingsOk,
      ui: 'detail',
    },

    updateUserSettings: {
      method: HttpMethod.patch,
      path: '/',
      summary: 'Update user settings',
      body: settingsSchemas.ref.UpdateUserSettingsBody,
      response: settingsSchemas.ref.UserSettingsOk,
      ui: 'update',
    },

    updateNotificationSettings: {
      method: HttpMethod.patch,
      path: '/notifications',
      summary: 'Update notification settings',
      body: settingsUpdateBodySchemas.ref.UpdateNotificationSettingsBody,
      response: settingsSchemas.ref.UserSettingsOk,
      ui: 'update',
    },

    updatePrivacySettings: {
      method: HttpMethod.patch,
      path: '/privacy',
      summary: 'Update privacy settings',
      body: settingsUpdateBodySchemas.ref.UpdatePrivacySettingsBody,
      response: settingsSchemas.ref.UserSettingsOk,
      ui: 'update',
    },

    updateDisplaySettings: {
      method: HttpMethod.patch,
      path: '/display',
      summary: 'Update display settings',
      body: settingsUpdateBodySchemas.ref.UpdateDisplaySettingsBody,
      response: settingsSchemas.ref.UserSettingsOk,
      ui: 'update',
    },
  },
});

export const userSettingsContract = {
  userSettings,
  settingsProps,
  settingsCompositeSchemas,
  settingsPublicSchemas,
  settingsUpdateBodySchemas,
  settingsSchemas,
};
