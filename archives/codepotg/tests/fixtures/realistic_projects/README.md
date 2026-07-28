# Realistic Template-Pack Fixtures

These fixtures are derived from production-oriented Nest backend, Next server-action, and Dart API-client template packs. They intentionally run against the large canonical `tests/fixtures/openapi.json` document rather than the small nine-file smoke fixture.

The integration test copies and sanitizes only branding fields (`info` and `servers`) into a temporary `Northstar Platform API`; the complete resource, schema, operation, entity, frontend, access, and extension structure remains unchanged.

Run visible generation from `packages/python/codepotg`:

```bash
python scripts/generate_realistic_fixtures.py --pack all
```

Outputs appear under each project in `.generated-review/`. The directories are ignored because they contain hundreds of generated files, while representative exact snapshots are committed under `generated-examples/`.
