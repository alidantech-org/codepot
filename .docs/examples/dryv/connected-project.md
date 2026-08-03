# Human validation: connected Dryv project

The executable fixture lives at `packages/python/dryv/examples/manual/connected-project`. It is a real inspectable Dryv project rather than a pytest fixture. It validates two semantic authoring routes against the same packs and target plugins:

```text
A. public dryv.ir objects
B. dryv-author declarations
              |
              v
        canonical Contract
              |
              v
          Dryv runtime
              |
       +------+------+
       |             |
 TypeScript pack   Dart pack
       |             |
   Jinja engine   Jinja engine
       |             |
  tsc --noEmit    dart analyze
```

The purpose is to prove that software meaning belongs to the neutral contract while emitted text belongs to packs.

## 1. Synchronize the repository workspace

From the repository root:

```bash
uv sync --all-packages
cd packages/python/dryv/examples/manual/connected-project
rm -rf runs collision-output
```

`uv` manages the root `.venv` and installs all connected Python workspace members in editable mode. Do not create or activate a fixture-specific environment and do not install sibling packages manually.

## 2. Verify installed plugins

```bash
uv run --all-packages python verify_plugins.py
```

Expected IDs, each exactly once:

```text
sources: ir
targets: dart, typescript
engines: jinja
```

## Route A: direct public IR

### 3. Bootstrap the contract

```bash
uv run --all-packages python bootstrap_contract.py
```

Expected files:

```text
contract.codepot.json
contract.codepot.yaml
```

The script validates the contract and performs canonical JSON/YAML round trips.

### 4. Plan and generate

```bash
uv run --package dryv-cli dryv plan dryv.yaml | tee plan-direct.json
uv run --package dryv-cli dryv generate dryv.yaml --memory | tee memory-output-direct.json
uv run --package dryv-cli dryv generate dryv.yaml --destination runs/direct | tee write-report-direct.json
find runs/direct -type f | sort
```

Expected: 12 managed artifacts across TypeScript and Dart.

## Route B: typed Python authoring

### 5. Compile declarations

```bash
uv run --all-packages python bootstrap_author_contract.py
```

Expected files:

```text
contract.author.codepot.json
contract.author.codepot.yaml
```

The authoring package creates an in-memory public `Contract`; the canonical runtime codec writes the optional transport files used by this manual fixture.

### 6. Plan and generate

```bash
uv run --package dryv-cli dryv plan dryv-author.yaml | tee plan-author.json
uv run --package dryv-cli dryv generate dryv-author.yaml --memory | tee memory-output-author.json
uv run --package dryv-cli dryv generate dryv-author.yaml --destination runs/author | tee write-report-author.json
find runs/author -type f | sort
```

The author route should produce the same 12 target paths as the direct route. Content differences must be explainable by intentional source metadata, tags, bindings, or banners.

## 7. Compare representative outputs

```bash
diff -u \
  runs/direct/typescript/src/models/user.ts \
  runs/author/typescript/src/models/user.ts || true

diff -u \
  runs/direct/dart/lib/models/user.dart \
  runs/author/dart/lib/models/user.dart || true
```

## 8. Compile generated TypeScript

```bash
for ROUTE in direct author
do
  echo "== TypeScript: $ROUTE =="
  (
    cd "runs/$ROUTE/typescript"
    npm install
    npm run typecheck
  )
done
```

Acceptance: both routes pass `tsc --noEmit` without editing generated source.

## 9. Analyze generated Dart

```bash
for ROUTE in direct author
do
  echo "== Dart: $ROUTE =="
  (
    cd "runs/$ROUTE/dart"
    dart pub get
    dart format --output=none --set-exit-if-changed lib
    dart analyze
  )
done
```

Acceptance: both routes format and analyze successfully.

## 10. Prove deterministic regeneration

```bash
find runs/direct/typescript/src runs/direct/dart/lib -type f -print0 \
  | sort -z | xargs -0 sha256sum > before-direct.sha256
uv run --package dryv-cli dryv generate dryv.yaml --destination runs/direct \
  > rerun-report-direct.json

find runs/direct/typescript/src runs/direct/dart/lib -type f -print0 \
  | sort -z | xargs -0 sha256sum > after-direct.sha256
diff -u before-direct.sha256 after-direct.sha256
```

Expected: no differences and all write decisions are `leave`.

## 11. Prove managed-file protection

```bash
cp runs/direct/typescript/src/models/user.ts /tmp/dryv-user.ts
printf '\n// HUMAN EDIT THAT MUST BE PROTECTED\n' \
  >> runs/direct/typescript/src/models/user.ts

set +e
uv run --package dryv-cli dryv generate dryv.yaml --destination runs/direct
EDIT_EXIT=$?
set -e

echo "exit=$EDIT_EXIT"
tail -n 4 runs/direct/typescript/src/models/user.ts
```

Acceptance:

- generation exits non-zero;
- the manual edit remains present;
- ownership state remains unchanged;
- no partial output is committed.

Recover:

```bash
cp /tmp/dryv-user.ts runs/direct/typescript/src/models/user.ts
uv run --package dryv-cli dryv generate dryv.yaml --destination runs/direct
```

## 12. Prove stale managed-file cleanup

```bash
uv run --all-packages python bootstrap_contract.py --without-ticket
uv run --package dryv-cli dryv generate dryv.yaml --destination runs/direct

test ! -f runs/direct/typescript/src/models/ticket.ts
test ! -f runs/direct/dart/lib/models/ticket.dart
```

Restore the complete contract:

```bash
uv run --all-packages python bootstrap_contract.py
uv run --package dryv-cli dryv generate dryv.yaml --destination runs/direct
```

## 13. Prove unmanaged collision protection

```bash
rm -rf collision-output
mkdir -p collision-output/typescript/src/models
printf 'UNMANAGED HUMAN FILE\n' > collision-output/typescript/src/models/user.ts

set +e
uv run --package dryv-cli dryv generate dryv.yaml --destination collision-output
COLLISION_EXIT=$?
set -e

echo "exit=$COLLISION_EXIT"
cat collision-output/typescript/src/models/user.ts
```

Acceptance:

- generation exits non-zero;
- the unmanaged file is unchanged;
- no surrounding partial generation is committed.

## Acceptance checklist

```text
[ ] ir/typescript/dart/jinja entry points loaded exactly once
[ ] direct public IR contract bootstrapped and round-tripped
[ ] typed Python authoring contract compiled
[ ] both plans contain 12 artifacts
[ ] both memory renders succeeded
[ ] both filesystem generations succeeded
[ ] generated TypeScript passed type checking
[ ] generated Dart passed formatting and analysis
[ ] deterministic regeneration produced no content differences
[ ] manually modified managed file was protected
[ ] unchanged stale managed files were removed
[ ] unmanaged output collision was protected
```
