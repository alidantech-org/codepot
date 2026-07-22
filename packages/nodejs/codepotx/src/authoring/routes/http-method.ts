export const HttpMethod = { get: 'GET', post: 'POST', put: 'PUT', patch: 'PATCH', delete: 'DELETE', options: 'OPTIONS', head: 'HEAD' } as const;
export type HttpMethod = (typeof HttpMethod)[keyof typeof HttpMethod];
