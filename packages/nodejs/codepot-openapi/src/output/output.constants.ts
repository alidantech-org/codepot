import { PackageOutputFormat } from '../config/package-config.types.js';

export const DefaultOutputConfig = {
  folder: 'sdk/openapi',
  filePrefix: 'openapi',
  debugFilePrefix: 'contract-debug',
  formats: [PackageOutputFormat.json, PackageOutputFormat.yaml],
} as const;

export const ContentType = {
  json: 'application/json',
  multipartFormData: 'multipart/form-data',
  formUrlEncoded: 'application/x-www-form-urlencoded',
  octetStream: 'application/octet-stream',
  textPlain: 'text/plain',
  textHtml: 'text/html',
  pdf: 'application/pdf',
  png: 'image/png',
  jpeg: 'image/jpeg',
  webp: 'image/webp',
  svg: 'image/svg+xml',
} as const;

export type ContentType = (typeof ContentType)[keyof typeof ContentType];
