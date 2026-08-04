# Dart API Client Fixture Pack

This generic fixture generates Dart models, DTOs, enums, endpoint constants, feature clients, routes, and package entry points from the large canonical OpenAPI fixture.

The checked-in templates were derived from a production-oriented pack and deliberately contain no real product or company branding. The integration test creates a fictional `Northstar Platform API` input while preserving the full real-world contract shape.

Generate inspectable output from `packages/python/codepotg`:

```bash
python scripts/generate_realistic_fixtures.py --pack dart_client
```

Generated files appear in `.generated-review/`.
