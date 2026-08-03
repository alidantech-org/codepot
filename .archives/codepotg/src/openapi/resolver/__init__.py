"""OpenAPI resolver layer.

This layer provides standard OpenAPI resolution capabilities without any
code-generation-specific logic. It answers questions about the OpenAPI
specification itself:

- What does this $ref point to?
- Is this a schema ref, response ref, requestBody ref, or parameter ref?
- What schemas are inside this content object?
- What content types does this request/response support?
- What component refs are missing?

This layer does NOT make code-generation decisions such as:
- Is this a Dart DTO?
- Which resource owns this?
- Which folder should this emit into?
- Is this body/query/response role?

Those decisions belong in the inference layer.

Modules:
- pointers: JSON pointer parsing and walking
- components: Component index and generic component lookup
- content: Standard OpenAPI media content extraction
- parameters: Standard parameter resolution and schema refs
- request_bodies: Standard requestBody resolution
- responses: Standard response resolution
"""
