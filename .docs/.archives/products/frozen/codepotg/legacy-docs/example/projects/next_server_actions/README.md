# Next Server Actions Fixture Pack

This generic fixture generates Next.js server actions, API helpers, route constants, DTOs, enums, and server-side barrels from the large canonical OpenAPI fixture.

The checked-in templates were derived from a production-oriented pack and deliberately contain no real product or company branding. The integration test creates a fictional `Northstar Platform API` input while preserving the full real-world contract shape.

Generate inspectable output from `packages/python/codepotg`:

```bash
python scripts/generate_realistic_fixtures.py --pack next_server_actions
```

Generated files appear in `.generated-review/`.
