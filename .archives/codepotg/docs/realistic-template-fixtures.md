# Realistic Template Fixtures

CodepotG has two separate fixture tiers. They must not be described as equivalent.

## Smoke fixtures

`tests/fixtures/projects/typescript` and `tests/fixtures/projects/dart` use the small
`project_openapi.yaml` contract. They generate nine files and validate basic configuration,
path expansion, template variables, cache reuse, and language adapter compatibility.

They are smoke tests. They are not performance or production-pack evidence.

## Realistic fixtures

`tests/fixtures/realistic_projects` contains three production-oriented packs:

- `nest_backend` — Nest controllers, services, modules, use cases, TypeORM entities, DTOs,
  enums, routes, and barrels;
- `next_server_actions` — Next server actions, API helpers, routes, DTOs, enums, and barrels;
- `dart_client` — Dart models, DTOs, enums, routes, endpoint constants, feature clients, and
  package entry points.

The integration gate copies `tests/fixtures/openapi.json`, which is the large canonical
real-world contract, and sanitizes only branding values into a fictional Northstar API. The
resource, operation, schema, entity, frontend, access, relation, and dependency structure is
preserved.

The realistic gate verifies:

- the generated input remains substantial and retains at least 100 paths and 100 schemas;
- every planned output path is unique;
- every planned file is physically written;
- each pack emits a substantial project rather than nine toy files;
- normalized schema, codegen, and entity roots are consumed by real templates;
- the Nest entity and use-case barrels are resource-scoped and collision-free;
- the SQLite/JSONL cache is reused on a second generation;
- real company and product branding is absent from committed fixture packs;
- representative generated examples remain inspectable in the repository.

Serialized byte size is recorded as supporting evidence, not used as the sole definition of a
realistic contract. Formatting or sanitization changes may alter byte size without changing the
contract's resource, operation, and schema coverage.

## Generate visible output

From `packages/python/codepotg`:

```bash
python scripts/generate_realistic_fixtures.py --pack all --clean
```

Outputs are written to each project under `.generated-review/` instead of a temporary
profiler directory.

## Profile a real pack

First prepare the fixture input:

```bash
python scripts/generate_realistic_fixtures.py --pack nest_backend --clean
```

Then profile with the real templates and a persistent workspace:

```bash
python scripts/profile_memory.py \
  tests/fixtures/realistic_projects/nest_backend/openapi.generated.json \
  --language typescript \
  --templates tests/fixtures/realistic_projects/nest_backend/templates \
  --workspace tests/fixtures/realistic_projects/nest_backend/.profile-review \
  --emit \
  --json
```

A profile using the default debug pack must be labeled synthetic and cannot by itself prove
Nest, Next, or Dart pack performance.
