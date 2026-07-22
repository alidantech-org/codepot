export const HttpMethod = {
  get: 'get',
  post: 'post',
  put: 'put',
  patch: 'patch',
  delete: 'delete',
} as const;

export type HttpMethod = (typeof HttpMethod)[keyof typeof HttpMethod];
