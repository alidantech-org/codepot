Yes. I would simplify it like this:

```txt
security.protected = true/false
security.auth      = OpenAPI-style auth requirement ref
security.roleSets  = role-set refs
security.guards    = guard refs
```

Do **not** put `protected` under `auth`.

## Clean top-level shape

```yaml
security:
  defaults:
    protected: true
    auth:
      $ref: "#/security/auth/bearer"
    roleSets: []
    guards: []

  schemes:
    bearer:
      type: http
      scheme: bearer
      bearerFormat: JWT

    sessionCookie:
      type: apiKey
      in: cookie
      name: sid

    apiKey:
      type: apiKey
      in: header
      name: x-api-key

    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/oauth/authorize
          tokenUrl: https://auth.example.com/oauth/token
          scopes:
            users:read: Read users
            users:write: Write users

  auth:
    bearer:
      mode: any
      schemes:
        - scheme:
            $ref: "#/security/schemes/bearer"

    session:
      mode: any
      schemes:
        - scheme:
            $ref: "#/security/schemes/sessionCookie"

    bearer_or_session:
      mode: any
      schemes:
        - scheme:
            $ref: "#/security/schemes/bearer"
        - scheme:
            $ref: "#/security/schemes/sessionCookie"

    bearer_and_api_key:
      mode: all
      schemes:
        - scheme:
            $ref: "#/security/schemes/bearer"
        - scheme:
            $ref: "#/security/schemes/apiKey"

    oauth_users_write:
      mode: any
      schemes:
        - scheme:
            $ref: "#/security/schemes/oauth2"
          scopes:
            - users:write
```

## Roles and guards stay separate

```yaml
security:
  roleSources:
    tenant_role:
      source:
        $ref: "#/schemas/entities/tenant_member/fields/role"
      enum:
        $ref: "#/properties/enums/tenant_role"

  roleSets:
    tenant_member:
      role:
        $ref: "#/security/roleSources/tenant_role"
      values:
        - $ref: "#/properties/enums/tenant_role/values/member"
        - $ref: "#/properties/enums/tenant_role/values/admin"
        - $ref: "#/properties/enums/tenant_role/values/owner"

    tenant_admin:
      role:
        $ref: "#/security/roleSources/tenant_role"
      values:
        - $ref: "#/properties/enums/tenant_role/values/admin"
        - $ref: "#/properties/enums/tenant_role/values/owner"

  contexts:
    auth_user:
      target: context.user
      schema:
        $ref: "#/schemas/contexts/auth_user_context"

    tenant:
      target: context.tenant
      schema:
        $ref: "#/schemas/contexts/tenant_context"

  guards:
    auth_user:
      handler: authUserGuard
      outputs:
        - $ref: "#/security/contexts/auth_user"

    tenant:
      handler: tenantGuard
      outputs:
        - $ref: "#/security/contexts/tenant"
```

## Resource default

```yaml
resources:
  users:
    defaults:
      security:
        protected: true
        auth:
          $ref: "#/security/auth/bearer"
        roleSets:
          - $ref: "#/security/roleSets/tenant_member"
        guards:
          - $ref: "#/security/guards/auth_user"
          - $ref: "#/security/guards/tenant"
```

## Route override

```yaml
routes:
  "/auth/login":
    post:
      security:
        protected: false
      responses:
        200:
          $ref: "#/responses/custom/login_response"

  "/tenants/{tenantId}/users":
    post:
      operation:
        $ref: "#/resources/users/operations/create_user"

      security:
        protected: true
        auth:
          $ref: "#/security/auth/bearer"
        roleSets:
          - $ref: "#/security/roleSets/tenant_admin"
        guards:
          - $ref: "#/security/guards/auth_user"
          - $ref: "#/security/guards/tenant"

      body:
        schema:
          $ref: "#/schemas/models/user_create"
        contentType:
          $ref: "#/contentTypes/json"

      responses:
        201:
          $ref: "#/responses/custom/user_response"
```

## Locked meanings

```txt
security.schemes
  OpenAPI-compatible auth schemes: bearer, cookie, apiKey, oauth2, openIdConnect.

security.auth
  Reusable auth requirements built from security.schemes.

security.defaults.protected
  Default login requirement.

route.security.protected
  true = authentication required.
  false = public route.

route.security.auth
  Ref to one auth requirement.

route.security.roleSets
  Refs only. No hard-coded roles.

route.security.guards
  Refs only. No hard-coded guard names.
```

## Compiler rules

```txt
1. Every normalized route must have security.protected true/false.

2. If protected is false:
   - auth must be omitted
   - roleSets must be empty
   - guards must be empty

3. If protected is true:
   - auth must resolve from route, resource default, or security default
   - roleSets may be empty
   - guards may be empty

4. route.security.auth must be a ref to #/security/auth/*.

5. route.security.roleSets items must be refs to #/security/roleSets/*.

6. route.security.guards items must be refs to #/security/guards/*.

7. security.schemes should compile directly to OpenAPI securitySchemes.

8. security.auth should compile to OpenAPI operation security requirements.
```

This gives you a simple route shape while still borrowing the best part of OpenAPI security.
